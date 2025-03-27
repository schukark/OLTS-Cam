use serde::{Deserialize, Serialize};
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
