#![deny(missing_docs)]
#![deny(clippy::missing_docs_in_private_items)]
//! "Object Location Tracking System with Camera"
//! provides functionlity to deploy a system to observe
//! your belongings at home through a camera and
//! query a telegram bot about it

use dotenv::dotenv;
use futures::future::join_all;

mod bot;
mod errors;
mod models;
mod requests;

use lazy_static::lazy_static;
use reqwest::Client;

lazy_static! {
    static ref CLIENT: Client = Client::new();
}

/// Python desktop client server address
pub const ADDRESS: &str = "127.0.0.1";
/// Python desktop client server port
pub const PORT: u32 = 19841;

#[tokio::main]
async fn main() {
    dotenv().ok();

    pretty_env_logger::init();

    let bot_task = tokio::spawn(bot::run_bot());

    join_all(vec![bot_task]).await;
}
