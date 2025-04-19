//! Models module defines the models that are used in the exchange between the rust bot client and the python api server

use crate::errors::ModelError;
use serde::{Deserialize, Serialize};
use serde_json::to_string_pretty;
use std::fmt::Display;

/// A simple wrapper for (key, value) pairs in settings
#[derive(Debug, Serialize, Deserialize, Eq, PartialEq)]
struct SettingsInner {
    /// Settings' name
    key: String,
    /// Value of the current settings' parameter
    value: String,
}

/// Different types of settings receivers (different configurable components)
#[derive(Debug, Serialize, Deserialize, Eq, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum Receiver {
    /// Camera variant
    Camera,
    /// Database variant
    Db,
    /// Filesystem variant
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

/// Settings model to interchange with the python desktop client
#[derive(Debug, Serialize, Deserialize, Eq, PartialEq)]
pub struct Settings {
    /// Type of settings' receiver
    receiver: Receiver,
    /// The settings in key-value pairs
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

/// A model representing a photo with an object on it for python interoperability
#[derive(Debug, Serialize, Deserialize)]
pub struct ObjectPhoto {
    /// Height of the image
    height: u32,
    /// Width of the image
    width: u32,
    /// Base64 encoded image
    image: String,
}

impl ObjectPhoto {
    /// Getter for the image field
    pub fn image(&self) -> &str {
        &self.image
    }
}
