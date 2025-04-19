#![warn(missing_docs)]

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

pub const ADDRESS: &str = "127.0.0.1";
pub const PORT: u32 = 19841;

#[tokio::main]
async fn main() {
    dotenv().ok();

    pretty_env_logger::init();

    let bot_task = tokio::spawn(bot::run_bot());

    join_all(vec![bot_task]).await;
}
