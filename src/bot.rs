//! This module provides all the functionality of the bot according to the task
use crate::requests::*;

use teloxide::{
    adaptors::throttle::{Limits, Throttle},
    prelude::*,
    types::InputFile,
    utils::command::BotCommands,
};

/// Python desktop client server address and port
const ADDRESS_STR: &str = "127.0.0.1:19841";

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

async fn answer(bot: Throttle<Bot>, msg: Message, cmd: Command) -> ResponseResult<()> {
    match cmd {
        Command::Help => {
            bot.send_message(msg.chat.id, Command::descriptions().to_string())
                .await?
        }
        Command::CurrentState => {
            bot.send_message(msg.chat.id, String::from("current-state"))
                .await?
        }
        Command::WhereIs(object_name) => {
            let object = get_object(ADDRESS_STR, object_name).await;

            if let Ok(object_inner) = object {
                let conversion_result = convert_to_image(object_inner.image());
                if conversion_result.is_err() {
                    bot.send_message(msg.chat.id, "Incorrect base64 image string received")
                        .await?
                } else {
                    bot.send_photo(msg.chat.id, conversion_result.expect("CAN'T FAIL"))
                        .await?
                }
            } else {
                bot.send_message(msg.chat.id, "No such item found").await?
            }
        }
        Command::GetSettings(receiver) => {
            let rcv = receiver.try_into();

            if rcv.is_err() {
                bot.send_message(msg.chat.id, "Incorrect receiver specified")
                    .await?;
            }

            let rcv = rcv.unwrap();

            let result = get_settings(ADDRESS_STR, rcv).await;

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

            let result = change_settings(ADDRESS_STR, settings_formatted).await;
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

/// Starts the bot from the environmental variable configuration
pub async fn run_bot() {
    log::info!("Starting the bot...");

    let bot = Bot::from_env().throttle(Limits::default());

    Command::repl(bot, answer).await;
}
