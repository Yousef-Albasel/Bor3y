# Discord AI Bot with Gemini

## Overview

A Discord bot application that integrates Google's Gemini AI to provide intelligent responses when mentioned in Discord channels. The bot uses discord.py for Discord integration and Google's GenAI library to generate AI-powered responses. The application is designed as a simple, single-file bot with built-in logging, error handling, and status monitoring capabilities.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Framework
- **Discord.py Framework**: Uses the discord.py library with a commands.Bot class architecture for handling Discord interactions
- **Event-Driven Design**: Implements Discord event handlers (on_ready, on_message) to respond to Discord events
- **Command System**: Built-in command prefix system ('!') for bot commands and status monitoring

### AI Integration
- **Google Gemini API**: Primary AI service for generating intelligent responses to user mentions
- **Asynchronous Processing**: Handles AI API calls asynchronously to prevent blocking Discord operations
- **Error Handling**: Graceful degradation when AI services are unavailable

### Configuration Management
- **Environment Variables**: Uses python-dotenv for secure configuration management
- **Secrets Handling**: Discord bot tokens and API keys stored in environment variables
- **Fallback Mechanisms**: Built-in error handling for missing or invalid API credentials

### Logging and Monitoring
- **Dual Logging**: Outputs to both file (discord_bot.log) and console for debugging
- **Structured Logging**: Timestamped logs with appropriate log levels for monitoring
- **Status Commands**: Built-in commands for monitoring bot health and connectivity

### Message Processing
- **Mention Detection**: Responds specifically to bot mentions in Discord channels
- **Content Filtering**: Processes message content with appropriate Discord intents
- **Response Generation**: Integrates user messages with Gemini AI for contextual responses

## External Dependencies

### Core Services
- **Discord API**: Primary platform integration for bot functionality
- **Google Gemini AI**: AI service for generating intelligent responses via Google GenAI library

### Python Libraries
- **discord.py**: Discord bot framework and API wrapper
- **google-genai**: Official Google Generative AI Python library
- **python-dotenv**: Environment variable management for configuration

### Infrastructure Requirements
- **Discord Developer Portal**: Required for bot token generation and permissions
- **Google AI Studio**: Required for Gemini API key generation
- **File System**: Local logging to discord_bot.log file