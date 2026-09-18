"""The request and response shapes described in `../API.md`.

A model never leaves a handler as is: it goes through a schema, which decides what gets
published — that is what keeps a new column (a `password_hash`, say) out of a response.
"""
