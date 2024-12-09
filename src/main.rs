use teloxide::{prelude::*, utils::command::BotCommands};

#[derive(Clone, BotCommands)]
#[command(
    rename_rule = "lowercase",
    description = "These commands are supported:"
)]
enum Command {
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

#[tokio::main]
async fn main() {
    pretty_env_logger::init();
    log::info!("Starting throw dice bot...");

    let bot = Bot::from_env();

    Command::repl(bot, answer).await;
}

async fn answer(bot: Bot, msg: Message, cmd: Command) -> ResponseResult<()> {
    match cmd {
        Command::CurrentState => {
            bot.send_message(msg.chat.id, String::from("current-state"))
                .await?
        }
        Command::WhereIs(object_name) => {
            bot.send_message(msg.chat.id, object_name.to_string())
                .await?
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
