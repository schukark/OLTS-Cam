use crate::errors::ModelError;
use serde::{Deserialize, Serialize};
use serde_json::to_string_pretty;
use std::fmt::Display;

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

impl TryFrom<String> for Receiver {
    type Error = ModelError;

    fn try_from(value: String) -> Result<Self, Self::Error> {
        match value.as_str() {
            "db" => Ok(Receiver::Db),
            "camera" => Ok(Receiver::Camera),
            "fs" => Ok(Receiver::Fs),
            x => Err(ModelError::InvalidReceiver(format!(
                "{x} is not a valid receiver"
            ))),
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Settings {
    receiver: Receiver,
    settings: Vec<SettingsInner>,
}

impl Display for Settings {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let rcv_emoji = match &self.receiver {
            Receiver::Camera => "📷",
            Receiver::Db => "⛁",
            Receiver::Fs => "📁",
        };

        write!(
            f,
            "Settings for {} are: {}",
            rcv_emoji,
            to_string_pretty(self).unwrap()
        )
    }
}

impl TryInto<Settings> for String {
    type Error = ModelError;

    fn try_into(self) -> Result<Settings, Self::Error> {
        unimplemented!()
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ObjectPhoto {
    height: u32,
    width: u32,
    image: String,
}

impl ObjectPhoto {
    pub fn get_image(&self) -> &str {
        &self.image
    }
}
