use dotenv::dotenv;
use futures::future::join_all;

mod bot;
mod listenner;
mod requests;

#[tokio::main]
async fn main() {
    dotenv().ok();

    pretty_env_logger::init();

    let bot_task = tokio::spawn(bot::run_bot());
    let listenner_task = tokio::spawn(listenner::listen_json());

    join_all(vec![bot_task, listenner_task]).await;
}
