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

    #[command(description = "Change settings to the camera")]
    SettingsCamera(String),

    #[command(description = "Change settings to the filesystem")]
    SettingsFilesystem(String),

    #[command(description = "Change settings to the CV model")]
    SettingsCVModel(String),
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
        Command::SettingsCamera(options) => {
            bot.send_message(
                msg.chat.id,
                format!(
                    "The settings options for the camera are: {}",
                    options.split_whitespace().collect::<Vec<_>>().join("; ")
                ),
            )
            .await?
        }
        Command::SettingsFilesystem(options) => {
            bot.send_message(
                msg.chat.id,
                format!(
                    "The settings options for the filesystem are: {}",
                    options.split_whitespace().collect::<Vec<_>>().join("; ")
                ),
            )
            .await?
        }
        Command::SettingsCVModel(options) => {
            bot.send_message(
                msg.chat.id,
                format!(
                    "The settings options for the cvmodel are: {}",
                    options.split_whitespace().collect::<Vec<_>>().join("; ")
                ),
            )
            .await?
        }
    };

    Ok(())
}

pub async fn run_bot() {
    log::info!("Starting the bot...");

    let bot = Bot::from_env().throttle(Limits::default());

    Command::repl(bot, answer).await;
}
