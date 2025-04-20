#![deny(missing_docs)]
#![deny(clippy::missing_docs_in_private_items)]
#![feature(if_let_guard)]
//! "Object Location Tracking System with Camera"
//! provides functionlity to deploy a system to observe
//! your belongings at home through a camera and
//! query a telegram bot about it

use dotenv::dotenv;
use futures::future::join_all;

mod bot;
mod errors;
mod models;
mod api_client;

/// The main function that runs the bot
#[tokio::main]
pub async fn main() {
    dotenv().ok();

    pretty_env_logger::init();

    let bot_task = tokio::spawn(bot::run_bot());

    join_all(vec![bot_task]).await;
}
