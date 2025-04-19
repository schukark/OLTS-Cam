//! This module provides all the functionality of the bot according to the task
use crate::requests::*;

use teloxide::{
    dispatching::UpdateHandler, prelude::*, types::InputFile, utils::command::BotCommands,
};

/// Returns the API address as "host:port", defaulting to 127.0.0.1:19841
fn get_api_address() -> String {
    let result = std::env::var("API_ADDRESS").unwrap_or_else(|_| "127.0.0.1:19841".to_string());
    dbg!(&result);

    result
}

use base64::{prelude::*, DecodeError};

/// This function takes a base64 encoded image and returns the decoded version of it (if it succeedes)
fn convert_to_image(base64_image: &str) -> Result<InputFile, DecodeError> {
    Ok(InputFile::memory(BASE64_STANDARD.decode(base64_image)?))
}

/// Command implementation for the bot (teloxide::utils::command::BotCommands)
#[derive(Clone, BotCommands)]
#[command(
    rename_rule = "lowercase",
    description = "These commands are supported:"
)]
enum Command {
    /// Help command that will output all available commands
    #[command(description = "List all available commands")]
    Help,

    /// Get the current state of the camera feed
    #[command(description = "Display current objects")]
    CurrentState,

    /// Search for object
    #[command(description = "Search for object")]
    WhereIs(String),

    /// Get current settings for the chosen receiver
    #[command(description = "Get settings")]
    GetSettings(String),

    /// Change settings for a chosen receiver
    #[command(description = "Change settings")]
    ChangeSettings(String),
}

type HandlerResult = Result<(), Box<dyn std::error::Error + Send + Sync + 'static>>;

/// Function that determines what the bot will answer depending on the command used
async fn answer(bot: Bot, msg: Message, cmd: Command, api: ApiClient) -> HandlerResult {
    match cmd {
        Command::Help => {
            bot.send_message(msg.chat.id, Command::descriptions().to_string())
                .await?
        }
        Command::CurrentState => {
            let object = api.get_objects().await;

            if let Ok(object_inner) = object {
                match convert_to_image(object_inner.image()) {
                    Ok(photo) => bot.send_photo(msg.chat.id, photo).await?,
                    Err(_) => {
                        bot.send_message(msg.chat.id, "Incorrect base64 image string received")
                            .await?
                    }
                }
            } else {
                bot.send_message(msg.chat.id, "Error retrieving image")
                    .await?
            }
        }
        Command::WhereIs(ref object_name) => {
            let object = api.get_object(object_name).await;

            if let Ok(object_inner) = object {
                match convert_to_image(object_inner.image()) {
                    Ok(photo) => bot.send_photo(msg.chat.id, photo).await?,
                    Err(_) => {
                        bot.send_message(msg.chat.id, "Incorrect base64 image string received")
                            .await?
                    }
                }
            } else {
                bot.send_message(msg.chat.id, "Error retrieving image")
                    .await?
            }
        }
        Command::GetSettings(receiver) => {
            let rcv = receiver.try_into();

            if rcv.is_err() {
                bot.send_message(msg.chat.id, "Incorrect receiver specified")
                    .await?;
            }

            let rcv = rcv.unwrap();

            let result = api.get_settings(rcv).await;

            match result {
                Ok(settings) => {
                    bot.send_message(msg.chat.id, format!("Current settings are:\n{}", settings))
                        .await?
                }
                Err(_) => {
                    bot.send_message(msg.chat.id, "Couldn't get current settings")
                        .await?
                }
            }
        }
        Command::ChangeSettings(settings) => {
            let settings_formatted = serde_json::from_str(&settings);

            if settings_formatted.is_err() {
                bot.send_message(msg.chat.id, "Incorrectly formatted settings")
                    .await?;
            }

            let settings_formatted = settings_formatted.unwrap();

            let result = api.change_settings(settings_formatted).await;
            match result {
                Ok(_) => {
                    bot.send_message(msg.chat.id, "Settings changed successfully")
                        .await?
                }
                Err(_) => {
                    bot.send_message(msg.chat.id, "Failed to change settings")
                        .await?
                }
            }
        }
    };

    Ok(())
}

/// Handler
fn handler_tree() -> UpdateHandler<Box<dyn std::error::Error + Send + Sync + 'static>> {
    // A simple handler. But you need to make it into a separate thing!
    dptree::entry().branch(
        Update::filter_message()
            .branch(dptree::entry().filter_command::<Command>().endpoint(answer)),
    )
}

/// Starts the bot from the environmental variable configuration
pub async fn run_bot() {
    log::info!("Starting the bot...");

    let bot = Bot::from_env();
    let tree = dptree::entry().branch(handler_tree());
    let api = ApiClient::new(get_api_address());

    Dispatcher::builder(bot, tree)
        .enable_ctrlc_handler()
        .dependencies(dptree::deps![api.clone()])
        .build()
        .dispatch()
        .await;
}

#[cfg(test)]
mod tests {
    use super::*;
    use anyhow::Result;
    use httpmock::prelude::*;
    use teloxide_tests::{MockBot, MockMessageText};
    use tokio::time::{timeout, Duration};

    mod current_state_tests {
        use super::*;

        #[tokio::test]
        async fn test_erroneous_server() -> Result<()> {
            let server = MockServer::start_async().await;

            let mock = server.mock(|when, then| {
                when.method(GET).path("/objects");
                then.status(421).header("content-type", "application/json");
            });

            let api = ApiClient::new(server.address().to_string());

            let bot = MockBot::new(MockMessageText::new().text("/currentstate"), handler_tree());
            bot.dependencies(dptree::deps![api]);

            timeout(
                Duration::from_secs(1),
                bot.dispatch_and_check_last_text("Error retrieving image"),
            )
            .await?;
            mock.assert_async().await;

            Ok(())
        }

        #[tokio::test]
        async fn test_incorrect_base64() -> Result<()> {
            let server = MockServer::start_async().await;

            let body = "\"width\":224,\"height\":224,\"image\":\"aboba\"";
            let mock = server.mock(|when, then| {
                when.method(GET).path("/objects");
                then.status(200)
                    .header("content-type", "application/json")
                    .body(body);
            });

            let api = ApiClient::new(server.address().to_string());

            let bot = MockBot::new(MockMessageText::new().text("/currentstate"), handler_tree());
            bot.dependencies(dptree::deps![api]);

            timeout(
                Duration::from_secs(1),
                bot.dispatch_and_check_last_text("Incorrect base64 image string received"),
            )
            .await?;
            mock.assert_async().await;

            Ok(())
        }
    }
}
