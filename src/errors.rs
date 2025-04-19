use thiserror::Error;

#[derive(Error, Debug)]
pub enum ModelError {
    #[error("")]
    InvalidReceiver(String),
    #[error("")]
    InvalidSettings(String),
}
