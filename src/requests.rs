use std::fmt::Display;

use crate::{ADDRESS, CLIENT, PORT};
use reqwest::Error;

use serde::{Deserialize, Serialize};
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

impl Display for Receiver {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let name = match self {
            Receiver::Camera => "camera",
            Receiver::Db => "db",
            Receiver::Fs => "fs",
        };

        write!(f, "{}", name)
    }
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
    image: String,
}

pub async fn change_settings(settings: Settings) -> Result<(), Error> {
    let request_url = format!("http://{ADDRESS}:{PORT}/settings",);
    CLIENT.post(request_url).json(&settings).send().await?;

    Ok(())
}

pub async fn get_settings(receiver: Receiver) -> Result<Settings, Error> {
    let request_url = format!("http://{ADDRESS}:{PORT}/settings/{receiver}");

    let response = CLIENT.get(request_url).send().await?;

    let settings = response.json().await?;

    Ok(settings)
}

pub async fn get_object(name: String) -> Result<ObjectPhoto, Error> {
    let request_url = format!("http://{ADDRESS}:{PORT}/object/{name}");

    let response = CLIENT.get(request_url).send().await?;

    let object = response.json().await?;

    Ok(object)
}
