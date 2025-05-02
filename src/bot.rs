//! This module provides all the functionality of the bot according to the task
use crate::{api_client::*, errors::ModelError, models::Receiver};

use teloxide::{
    dispatching::UpdateHandler, prelude::*, types::InputFile, utils::command::BotCommands,
};

/// Returns the API address as "host:port", defaulting to 127.0.0.1:19841
fn get_api_address() -> String {
    log::trace!("Queried the api address");

    std::env::var("API_ADDRESS").unwrap_or_else(|_| "127.0.0.1:19841".to_string())
}

use base64::{prelude::*, DecodeError};

/// This function takes a base64 encoded image and returns the decoded version of it (if it succeedes)
fn convert_to_image(base64_image: &str) -> Result<InputFile, DecodeError> {
    log::trace!("Decoding image from base64");
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
            log::info!("Asked for list of all the commands");

            bot.send_message(msg.chat.id, Command::descriptions().to_string())
                .await?
        }
        Command::CurrentState => {
            log::info!("Asked for the current state");

            let object = api.get_objects().await;

            if let Ok(object_inner) = object {
                log::debug!("Successfully received an image");
                match convert_to_image(object_inner.image()) {
                    Ok(photo) => {
                        log::debug!("Successfully decoded the image from base64");
                        bot.send_photo(msg.chat.id, photo).await?
                    }
                    Err(_) => {
                        log::debug!("Couldn't decode from base64");
                        bot.send_message(msg.chat.id, "Incorrect base64 image string received")
                            .await?
                    }
                }
            } else {
                log::debug!("Coudn't receive image through API");
                bot.send_message(msg.chat.id, "Error retrieving image")
                    .await?
            }
        }
        Command::WhereIs(ref object_name) => {
            log::info!("Asked where an object {object_name} is");

            let object = api.get_object(object_name).await;

            if let Ok(object_inner) = object {
                log::debug!("Successfully received an image");
                match convert_to_image(object_inner.image()) {
                    Ok(photo) => {
                        log::debug!("Successfully decoded the image from base64");
                        bot.send_photo(msg.chat.id, photo).await?
                    }
                    Err(_) => {
                        log::debug!("Couldn't decode from base64");
                        bot.send_message(msg.chat.id, "Incorrect base64 image string received")
                            .await?
                    }
                }
            } else {
                log::debug!("Coudn't receive image through API");
                bot.send_message(msg.chat.id, "Error retrieving image")
                    .await?
            }
        }
        Command::GetSettings(receiver) => {
            log::info!("Asked for settings");

            let rcv = receiver.try_into();

            if rcv.is_err() {
                log::debug!("No such receiver");
                bot.send_message(msg.chat.id, "Incorrect receiver specified")
                    .await?;

                return Ok(());
            }

            let rcv = rcv.unwrap();

            let result = api.get_settings(rcv).await;

            match result {
                Ok(settings) => {
                    log::debug!("Correctly formatted settings");
                    bot.send_message(msg.chat.id, settings.to_string()).await?
                }
                Err(err) if let Some(_) = err.downcast_ref::<ModelError>() => {
                    log::debug!("Incorrectly formatted settings");
                    bot.send_message(msg.chat.id, "Incorrectly formatted settings")
                        .await?
                }
                Err(_) => {
                    log::debug!("Error retrieving settings from an API endpoint");
                    bot.send_message(msg.chat.id, "Error getting a response from an API server")
                        .await?
                }
            }
        }
        Command::ChangeSettings(settings) => {
            log::info!("Asked to change the settings");

            let settings_split = settings.split_whitespace().collect::<Vec<_>>();
            if settings_split.len() != 3 {
                log::debug!("Settings formatted incorrectly");
                bot.send_message(msg.chat.id, "Incorrectly formatted settings")
                    .await?;

                return Ok(());
            }

            let rcv = settings_split[0].to_owned();

            let rcv_new: Result<Receiver, _> = rcv.clone().try_into();

            if rcv_new.is_err() {
                log::debug!("Receiver formatted incorrectly");
                bot.send_message(
                    msg.chat.id,
                    "Reciever formatted incorrectly, should be one of: camera, db, fs",
                )
                .await?;

                return Ok(());
            }

            let name = settings_split[1].to_owned();
            let value = settings_split[2].to_owned();

            let settings = format!("{{\"receiver\":\"{rcv}\", \"settings\":[{{\"key\":\"{name}\",\"value\":\"{value}\"}}]}}");

            let settings_formatted = serde_json::from_str(&settings).unwrap();

            let result = api.change_settings(settings_formatted).await;
            match result {
                Ok(_) => {
                    log::debug!("Settings changed successfully");
                    bot.send_message(msg.chat.id, "Settings changed successfully")
                        .await?
                }
                Err(_) => {
                    log::debug!("Failed to change settings");
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
#[cfg_attr(coverage_nightly, coverage(off))]
pub async fn run_bot() {
    log::info!("Starting the bot...");

    let bot = Bot::from_env();
    log::debug!("Constructed bot from env variables");

    let tree = dptree::entry().branch(handler_tree());
    log::debug!("Constructed the dependency map");

    let api = ApiClient::new(get_api_address());
    log::debug!("Constructed an api client");

    Dispatcher::builder(bot, tree)
        .enable_ctrlc_handler()
        .dependencies(dptree::deps![api.clone()])
        .build()
        .dispatch()
        .await;
}

#[cfg(test)]
#[cfg_attr(coverage_nightly, coverage(off))]
mod tests {
    use super::*;
    use anyhow::Result;
    use httpmock::prelude::*;
    use serial_test::serial;
    use teloxide_tests::{MockBot, MockMessageText};
    use tokio::time::{timeout, Duration};

    mod current_state_tests {
        use super::*;

        #[tokio::test]
        #[serial]
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
        #[serial]
        async fn test_incorrect_base64() -> Result<()> {
            let server = MockServer::start_async().await;

            let body = "{\"width\":224,\"height\":224,\"image\":\"aboba\"}";
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

        #[tokio::test]
        #[serial]
        async fn test_correct() -> Result<()> {
            let image = "c2hvcnQ=";

            let server = MockServer::start_async().await;

            let body = "{\"width\":224,\"height\":224,\"image\":\"".to_owned() + image + "\"}";
            let mock = server.mock(|when, then| {
                when.method(GET).path("/objects");
                then.status(200)
                    .header("content-type", "application/json")
                    .body(body);
            });

            let api = ApiClient::new(server.address().to_string());

            let bot = MockBot::new(MockMessageText::new().text("/currentstate"), handler_tree());
            bot.dependencies(dptree::deps![api]);

            timeout(Duration::from_secs(1), bot.dispatch()).await?;
            mock.assert_async().await;

            bot.get_responses()
                .sent_messages_photo
                .last()
                .expect("Should be a photo sent");

            Ok(())
        }
    }

    mod where_is_tests {
        use super::*;

        #[tokio::test]
        #[serial]
        async fn test_erroneous_server() -> Result<()> {
            let server = MockServer::start_async().await;

            let mock = server.mock(|when, then| {
                when.method(GET).path("/object/apple");
                then.status(421).header("content-type", "application/json");
            });

            let api = ApiClient::new(server.address().to_string());

            let bot = MockBot::new(
                MockMessageText::new().text("/whereis apple"),
                handler_tree(),
            );
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
        #[serial]
        async fn test_incorrect_base64() -> Result<()> {
            let server = MockServer::start_async().await;

            let body = "{\"width\":224,\"height\":224,\"image\":\"aboba\"}";
            let mock = server.mock(|when, then| {
                when.method(GET).path("/object/apple");
                then.status(200)
                    .header("content-type", "application/json")
                    .body(body);
            });

            let api = ApiClient::new(server.address().to_string());

            let bot = MockBot::new(
                MockMessageText::new().text("/whereis apple"),
                handler_tree(),
            );
            bot.dependencies(dptree::deps![api]);

            timeout(
                Duration::from_secs(1),
                bot.dispatch_and_check_last_text("Incorrect base64 image string received"),
            )
            .await?;
            mock.assert_async().await;

            Ok(())
        }

        #[tokio::test]
        #[serial]
        async fn test_correct() -> Result<()> {
            let image = "c2hvcnQ=";

            let server = MockServer::start_async().await;

            let body = "{\"width\":224,\"height\":224,\"image\":\"".to_owned() + image + "\"}";
            let mock = server.mock(|when, then| {
                when.method(GET).path("/object/apple");
                then.status(200)
                    .header("content-type", "application/json")
                    .body(body);
            });

            let api = ApiClient::new(server.address().to_string());

            let bot = MockBot::new(
                MockMessageText::new().text("/whereis apple"),
                handler_tree(),
            );
            bot.dependencies(dptree::deps![api]);

            timeout(Duration::from_secs(1), bot.dispatch()).await?;
            mock.assert_async().await;

            bot.get_responses()
                .sent_messages_photo
                .last()
                .expect("Should be a photo sent");

            Ok(())
        }
    }

    mod get_settings_tests {
        use crate::models::Settings;

        use super::*;

        #[tokio::test]
        #[serial]
        async fn test_incorrect_receiver() -> Result<()> {
            let server = MockServer::start_async().await;

            let api = ApiClient::new(server.address().to_string());

            let bot = MockBot::new(
                MockMessageText::new().text("/getsettings apple"),
                handler_tree(),
            );
            bot.dependencies(dptree::deps![api]);

            timeout(
                Duration::from_secs(1),
                bot.dispatch_and_check_last_text("Incorrect receiver specified"),
            )
            .await?;

            Ok(())
        }

        #[tokio::test]
        #[serial]
        async fn test_erroneous_server() -> Result<()> {
            let server = MockServer::start_async().await;

            let mock = server.mock(|when, then| {
                when.method(GET).path("/settings/camera");
                then.status(421).header("content-type", "application/json");
            });

            let api = ApiClient::new(server.address().to_string());

            let bot = MockBot::new(
                MockMessageText::new().text("/getsettings camera"),
                handler_tree(),
            );
            bot.dependencies(dptree::deps![api]);

            timeout(
                Duration::from_secs(1),
                bot.dispatch_and_check_last_text("Error getting a response from an API server"),
            )
            .await?;
            mock.assert_async().await;

            Ok(())
        }

        #[tokio::test]
        #[serial]
        async fn test_incorrect_response() -> Result<()> {
            let server = MockServer::start_async().await;

            let body =
                "{\"receiver\":\"camera\", \"settings_incorrect\":[{\"key\":\"FPS\",\"value\":\"30\"}]}";
            let mock = server.mock(|when, then| {
                when.method(GET).path("/settings/camera");
                then.status(200)
                    .header("content-type", "application/json")
                    .body(body);
            });

            let api = ApiClient::new(server.address().to_string());

            let bot = MockBot::new(
                MockMessageText::new().text("/getsettings camera"),
                handler_tree(),
            );
            bot.dependencies(dptree::deps![api]);

            timeout(
                Duration::from_secs(1),
                bot.dispatch_and_check_last_text("Incorrectly formatted settings"),
            )
            .await?;
            mock.assert_async().await;

            Ok(())
        }

        #[tokio::test]
        #[serial]
        async fn test_correct() -> Result<()> {
            let server = MockServer::start_async().await;

            let body =
                "{\"receiver\":\"camera\", \"settings\":[{\"key\":\"FPS\",\"value\":\"30\"}]}";
            let mock = server.mock(|when, then| {
                when.method(GET).path("/settings/camera");
                then.status(200)
                    .header("content-type", "application/json")
                    .body(body);
            });

            let api = ApiClient::new(server.address().to_string());

            let bot = MockBot::new(
                MockMessageText::new().text("/getsettings camera"),
                handler_tree(),
            );
            bot.dependencies(dptree::deps![api]);

            timeout(
                Duration::from_secs(1),
                bot.dispatch_and_check_last_text(
                    &serde_json::from_str::<Settings>(body).unwrap().to_string(),
                ),
            )
            .await?;
            mock.assert_async().await;

            Ok(())
        }
    }

    mod change_settings_tests {
        use super::*;

        #[tokio::test]
        #[serial]
        async fn test_incorrect_settings() -> Result<()> {
            let server = MockServer::start_async().await;

            let api = ApiClient::new(server.address().to_string());
            let body = "value value value value";
            let bot = MockBot::new(
                MockMessageText::new().text(format!("/changesettings {body}")),
                handler_tree(),
            );
            bot.dependencies(dptree::deps![api]);

            timeout(
                Duration::from_secs(1),
                bot.dispatch_and_check_last_text("Incorrectly formatted settings"),
            )
            .await?;

            Ok(())
        }

        #[tokio::test]
        #[serial]
        async fn test_fail() -> Result<()> {
            let server = MockServer::start_async().await;

            let body = "camera FPS 30";
            let mock = server.mock(|when, then| {
                when.method(POST).path("/settings");
                then.status(421)
                    .header("content-type", "application/json")
                    .body(body);
            });

            let api = ApiClient::new(server.address().to_string());

            let bot = MockBot::new(
                MockMessageText::new().text(format!("/changesettings {body}")),
                handler_tree(),
            );
            bot.dependencies(dptree::deps![api]);

            timeout(
                Duration::from_secs(1),
                bot.dispatch_and_check_last_text("Failed to change settings"),
            )
            .await?;
            mock.assert_async().await;

            Ok(())
        }

        #[tokio::test]
        #[serial]
        async fn test_correct() -> Result<()> {
            let server = MockServer::start_async().await;

            let body = "camera FPS 30";
            let mock = server.mock(|when, then| {
                when.method(POST).path("/settings");
                then.status(200)
                    .header("content-type", "application/json")
                    .body(body);
            });

            let api = ApiClient::new(server.address().to_string());

            let bot = MockBot::new(
                MockMessageText::new().text(format!("/changesettings {body}")),
                handler_tree(),
            );
            bot.dependencies(dptree::deps![api]);

            timeout(
                Duration::from_secs(1),
                bot.dispatch_and_check_last_text("Settings changed successfully"),
            )
            .await?;
            mock.assert_async().await;

            Ok(())
        }
    }
}
