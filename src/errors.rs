//! Errors module contains errors type that are used internally in the project

use thiserror::Error;

/// Inner error type for models parsing
#[derive(Error, Debug, PartialEq, Eq)]
pub enum ModelError {
    /// Invalid reciever type (if it is not one of the preconfigured ones)
    #[error("")]
    InvalidReceiver(String),

    /// Invalid settings
    #[error("")]
    InvalidSettings,
}

/// Inner error type for requests
#[derive(Error, Debug, PartialEq, Eq)]
pub enum RequestError {
    /// No such setting
    #[error("No such setting")]
    NoSuchSetting,

    /// No such model
    #[error("No such reciever")]
    NoSuchReceiver,

    /// Unknown error
    #[error("Unknown error")]
    UnknownError,
}
