AWS KMS Key Provider (HSM-backed signing)

- The `AWSKMSKeyProvider` class provides a minimal adapter for using an AWS KMS asymmetric key for signing (tally keys).
- It returns an adapter object with a `.sign(message)` method which delegates to `KMS.Sign`.
- To use in production, configure your settings and set the default provider via `voting.key_provider.set_default_key_provider(...)` at startup.

Notes:
- This POC requires `boto3`. Where `boto3` is not available the provider raises a clear error during initialization.
- For KMS usage, create an asymmetric key with `KeyUsage=SIGN_VERIFY` and `CustomerMasterKeySpec=RSA_2048` (or RSA_4096) and use its KeyId.
