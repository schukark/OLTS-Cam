#![deny(missing_docs)]
#![deny(clippy::missing_docs_in_private_items)]
#![feature(if_let_guard)]
#![cfg_attr(coverage_nightly, feature(coverage_attribute))]
//! "Object Location Tracking System with Camera"
//! provides functionlity to deploy a system to observe
//! your belongings at home through a camera and
//! query a telegram bot about it

use std::fs::File;

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
