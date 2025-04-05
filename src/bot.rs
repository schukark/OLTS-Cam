use crate::models;
use crate::models::*;
use crate::requests::*;
use std::sync::Arc;

use teloxide::{
    adaptors::throttle::{Limits, Throttle},
    prelude::*,
    types::InputFile,
    utils::command::BotCommands,
};

use base64::{prelude::*, DecodeError};

fn convert_to_image(base64_image: &str) -> Result<InputFile, DecodeError> {
    Ok(InputFile::memory(BASE64_STANDARD.decode(base64_image)?))
}

#[derive(Clone, BotCommands)]
#[command(
    rename_rule = "lowercase",
    description = "These commands are supported:"
)]
enum Command {
    #[command(description = "List all available commands")]
    Help,

    #[command(description = "Display current objects")]
    CurrentState,

    #[command(description = "Search for object")]
    WhereIs(String),

    #[command(description = "Get settings")]
    GetSettings(String),

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
            let object = get_object(object_name).await;

            if let Ok(object_inner) = object {
                let conversion_result = convert_to_image(&object_inner.get_image());
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
            if models::RECEIVER_VALUES.contains(&receiver) {
                let settings = get_settings(&receiver).await;
                bot.send_message(msg.chat.id, settings).await?
            } else {
                bot.send_message(msg.chat.id, "Invalid receiver").await?
            }
        }
        Command::ChangeSettings(settings) => {
            let settings_formatted = settings.try_into();

            if settings_formatted.is_err() {
                bot.send_message(msg.chat.id, "Incorrectly formatted settings")
                    .await?
            }

            let settings_formatted = settings_formatted.unwrap();

            let result = change_settings(settings_formatted).await;
            if result.is_ok() {
                bot.send_message(msg.chat.id, "Settings changed successfully")
                    .await?
            } else {
                bot.send_message(msg.chat.id, "Failed to change settings")
                    .await?
            }
        }
    };

    Ok(())
}

pub async fn run_bot() {
    log::info!("Starting the bot...");

    let bot = Bot::from_env().throttle(Limits::default());

    Command::repl(bot, answer).await;
}
