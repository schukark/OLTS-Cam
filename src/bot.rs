use crate::requests::*;
use std::sync::Arc;

use teloxide::{prelude::*, utils::command::BotCommands};

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

async fn answer(bot: Bot, msg: Message, cmd: Command) -> ResponseResult<()> {
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

            let message_text = if let Ok(_object_image) = object {
                "Recievied a message with an item"
            } else {
                "No such item found"
            };
            bot.send_message(msg.chat.id, message_text).await?
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

    let bot = Bot::from_env();
    let bot = Arc::new(bot);

    Command::repl(bot, answer).await;
}
