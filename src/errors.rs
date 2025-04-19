//! Errors module contains an error type that is used internally in the project

use thiserror::Error;

/// Inner error type for models parsing
#[derive(Error, Debug)]
pub enum ModelError {
    /// Invalid reciever type (if it is not one of the preconfigured ones)
    #[error("")]
    InvalidReceiver(String),

    /// Parsing error when converting a string to valid settings struct
    #[error("")]
    InvalidSettings(String),
}
