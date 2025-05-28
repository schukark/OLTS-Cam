#![deny(missing_docs)]
#![deny(clippy::missing_docs_in_private_items)]
#![feature(if_let_guard)]
#![cfg_attr(coverage_nightly, feature(coverage_attribute))]
//! "Object Location Tracking System with Camera"
//! provides functionlity to deploy a system to observe
//! your belongings at home through a camera and
//! query a telegram bot about it

use std::{fs::File, io::Read, time::Duration};

use anyhow::Result;
use chrono::Local;
use dotenv::dotenv;
use futures::future::join_all;
use std::io::Write;

mod api_client;
mod bot;
mod errors;
mod models;

/// The main function that runs the bot
#[tokio::main]
#[cfg_attr(coverage_nightly, coverage(off))]
pub async fn main() -> Result<()> {
    dotenv().ok();

    let token = loop {
        let mut buf = String::new();
        if File::open("settings/model_settings.json")
            .and_then(|mut f| f.read_to_string(&mut buf))
            .is_ok()
        {
            if let Ok(json) = serde_json::from_str::<serde_json::Value>(&buf) {
                if let Some(s) = json
                    .get("telegram_token")
                    .and_then(|v| v.as_str())
                    .filter(|s| !s.is_empty())
                {
                    break s.to_string();
                }
            }
        }
        tokio::time::sleep(Duration::from_secs(1)).await;
    };

    // 2) inject into process environment
    std::env::set_var("TELOXIDE_TOKEN", &token);

    let target = Box::new(File::create("log.txt").expect("Can't create file"));

    env_logger::Builder::new()
        .filter_level(log::LevelFilter::Info)
        .target(env_logger::Target::Pipe(target))
        .format(|buf, record| {
            writeln!(
                buf,
                "[{} {} {}:{}] {}",
                Local::now().format("%Y-%m-%d %H:%M:%S%.3f"),
                record.level(),
                record.file().unwrap_or("unknown"),
                record.line().unwrap_or(0),
                record.args()
            )
        })
        .init();

    let bot_task = tokio::spawn(bot::run_bot());

    join_all(vec![bot_task]).await;

    Ok(())
}
