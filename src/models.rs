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

const RECEIVER_VALUES: [&'static str; 3] = ["camera", "db", "fs"];

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
            to_string_pretty(&obj).unwrap()
        )
    }
}

impl TryInto<Settings> for String {
    type Error;

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
