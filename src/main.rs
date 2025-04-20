#![deny(missing_docs)]
#![deny(clippy::missing_docs_in_private_items)]
#![feature(if_let_guard)]
#![cfg_attr(coverage_nightly, feature(coverage_attribute))]
//! "Object Location Tracking System with Camera"
//! provides functionlity to deploy a system to observe
//! your belongings at home through a camera and
//! query a telegram bot about it

use dotenv::dotenv;
use futures::future::join_all;

mod api_client;
mod bot;
mod errors;
mod models;

/// The main function that runs the bot
#[tokio::main]
#[cfg_attr(coverage_nightly, coverage(off))]
pub async fn main() {
    dotenv().ok();

    pretty_env_logger::init();

    let bot_task = tokio::spawn(bot::run_bot());

    join_all(vec![bot_task]).await;
}
