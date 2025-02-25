// use base64::{engine::general_purpose::STANDARD, Engine as _};
use serde::{Deserialize, Serialize};
use std::convert::Infallible;

#[derive(Debug, Deserialize)]
pub struct RequestData {
    key: String,
    // Add more fields as required
}

#[derive(Debug, Serialize)]
pub struct ResponseData {
    message: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct SettingsInner {
    key: String,
    value: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub enum Receiver {
    Camera,
    Db,
    Fs,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Settings {
    receiver: Receiver,
    settings: Vec<SettingsInner>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ObjectPhoto {
    height: u32,
    width: u32,
    image: String
}

pub async fn handle_request(data: RequestData) -> Result<impl warp::Reply, Infallible> {
    println!("Received JSON: {:?}", data);

    let response = ResponseData {
        message: format!("Received key: {}", data.key),
    };

    Ok(warp::reply::json(&response))
}
