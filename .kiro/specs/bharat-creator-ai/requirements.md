# Requirements Document

## Introduction

Bharat Creator AI is a comprehensive AI-powered content creation suite specifically designed for Indian content creators. The system provides five specialized tools covering the complete content lifecycle: viral script generation, image/thumbnail creation, multi-dialect voice generation, content repurposing across platforms, and personalized brand outreach. Each tool leverages multi-agent AI pipelines to deliver high-quality, culturally relevant content optimized for Indian audiences and platforms.

## Requirements

### Requirement 1: Multi-Agent Script Generation System

**User Story:** As an Indian content creator, I want an AI system that can generate viral scripts for my content, so that I can create engaging videos optimized for different platforms and niches.

#### Acceptance Criteria

1. WHEN a user provides a basic topic and selects niche, platform, duration, and language THEN the system SHALL process the input through a 5-agent pipeline
2. WHEN Agent 1 (Prompt Refiner) receives user input THEN it SHALL generate a detailed master prompt using AWS Bedrock
3. WHEN Agent 2 (Researcher) receives the refined prompt THEN it SHALL conduct web research using Google Gemini with search grounding
4. WHEN Agent 3 (Trend Analyst) receives research data THEN it SHALL analyze current trends specific to the selected niche and platform
5. WHEN Agent 4 (Fact Checker) receives research findings THEN it SHALL validate facts and flag unverified claims
6. WHEN Agent 5 (Script Writer) receives all agent outputs THEN it SHALL generate a final viral script with hook, main content, CTA, hashtags, and metadata
7. WHEN the script generation is complete THEN the system SHALL display each agent's output in expandable sections
8. WHEN displaying the final script THEN the system SHALL include structured JSON output with all required components

### Requirement 2: Dual-Agent Image Generation System

**User Story:** As a content creator, I want to generate professional cover images and thumbnails for my content, so that I can create visually appealing posts without design skills.

#### Acceptance Criteria

1. WHEN a user provides an image description, style preference, and size THEN the system SHALL process it through a 2-agent pipeline
2. WHEN Agent 1 (Prompt Refiner) receives user input THEN it SHALL optimize the prompt using AWS Bedrock Claude
3. WHEN Agent 2 (Image Generator) receives the refined prompt THEN it SHALL generate an image using Amazon Titan Image Generator v1
4. WHEN image generation is complete THEN the system SHALL display the image with download functionality
5. WHEN a user selects a style preset THEN the system SHALL apply appropriate keywords and descriptions
6. WHEN generating images THEN the system SHALL support 7 style presets (modern, minimalist, bold, cinematic, neon, vintage, custom)
7. WHEN generating images THEN the system SHALL support 6 size options for different platform requirements

### Requirement 3: Multi-Dialect Voice Generation System

**User Story:** As an Indian content creator, I want to generate high-quality voiceovers in multiple Indian languages with different moods, so that I can create audio content for diverse audiences.

#### Acceptance Criteria

1. WHEN a user provides script text, language selection, and mood preference THEN the system SHALL route to appropriate TTS service
2. WHEN generating Hindi or English audio THEN the system SHALL use AWS Polly Neural engine with SSML mood control
3. WHEN generating regional Indian language audio THEN the system SHALL use Google Cloud TTS Wavenet
4. WHEN processing mood preferences THEN the system SHALL support 6 mood presets with prosody, rate, and pitch control
5. WHEN voice generation is complete THEN the system SHALL provide audio playback and MP3 download functionality
6. WHEN supporting languages THEN the system SHALL handle 9 Indian languages (Hindi, English, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam)
7. WHEN generating audio THEN the system SHALL optimize voice selection for each language and service

### Requirement 4: Content Repurposing System

**User Story:** As a content creator, I want to transform my long-form content into multiple platform-specific formats, so that I can maximize my content reach across different social media platforms.

#### Acceptance Criteria

1. WHEN a user provides long-form content THEN the system SHALL generate platform-specific versions for 4 platforms
2. WHEN repurposing for Instagram THEN the system SHALL create carousel slides with appropriate formatting
3. WHEN repurposing for Twitter/X THEN the system SHALL create a thread with character-limited tweets
4. WHEN repurposing for LinkedIn THEN the system SHALL create a professional formatted post
5. WHEN repurposing for YouTube Shorts THEN the system SHALL create a timestamped script
6. WHEN processing content THEN the system SHALL maintain platform-specific constraints and best practices
7. WHEN repurposing is complete THEN the system SHALL display all four formats with copy functionality

### Requirement 5: Cold DM Generation System

**User Story:** As a content creator, I want to generate personalized cold DMs for brand outreach, so that I can effectively pitch collaboration opportunities to potential sponsors.

#### Acceptance Criteria

1. WHEN a user provides brand information and collaboration details THEN the system SHALL generate a personalized cold DM
2. WHEN brand research is enabled THEN the system SHALL use Google Gemini with web search to gather brand information
3. WHEN generating DMs THEN the system SHALL create a 4-part structure (hook, value proposition, pitch, CTA)
4. WHEN DM generation is complete THEN the system SHALL provide the full DM, follow-up message, and outreach tips
5. WHEN creating subject lines THEN the system SHALL generate compelling email subject options
6. WHEN processing brand research THEN the system SHALL gather recent news, campaigns, and brand values
7. WHEN generating follow-up content THEN the system SHALL provide appropriate timing and messaging suggestions

### Requirement 6: Unified System Architecture

**User Story:** As a system administrator, I want a modular architecture that allows independent deployment and operation of each tool, so that the system is maintainable and scalable.

#### Acceptance Criteria

1. WHEN deploying the system THEN each module SHALL operate independently as a standalone Streamlit application
2. WHEN a module is accessed THEN it SHALL load configuration from the root .env file
3. WHEN modules interact with AI services THEN they SHALL use appropriate authentication and error handling
4. WHEN storing credentials THEN the system SHALL use secure credential management for all API keys
5. WHEN modules generate output THEN they SHALL save files to the designated outputs directory
6. WHEN the system starts THEN each module SHALL be accessible via its own Streamlit interface
7. WHEN modules fail THEN they SHALL provide meaningful error messages and graceful degradation

### Requirement 7: Indian Market Optimization

**User Story:** As an Indian content creator, I want AI tools that understand Indian culture, trends, and languages, so that my content resonates with local audiences.

#### Acceptance Criteria

1. WHEN generating scripts THEN the system SHALL use curated Indian trend data for 7 niches
2. WHEN analyzing trends THEN the system SHALL consider Indian time zones, festivals, and cultural events
3. WHEN generating hashtags THEN the system SHALL include region-specific and Hindi hashtags
4. WHEN creating content THEN the system SHALL optimize for Indian social media usage patterns
5. WHEN providing recommendations THEN the system SHALL consider Indian creator economy best practices
6. WHEN generating voice content THEN the system SHALL support authentic Indian language pronunciation
7. WHEN researching brands THEN the system SHALL focus on Indian market context and cultural sensitivity

### Requirement 8: Security and Privacy

**User Story:** As a user of the system, I want my data and API credentials to be secure, so that I can use the tools without privacy concerns.

#### Acceptance Criteria

1. WHEN storing API credentials THEN the system SHALL use environment variables and secure credential files
2. WHEN processing user content THEN the system SHALL not store personal data permanently
3. WHEN accessing external APIs THEN the system SHALL use proper authentication and rate limiting
4. WHEN handling generated content THEN the system SHALL provide secure download mechanisms
5. WHEN managing credentials THEN the system SHALL exclude sensitive files from version control
6. WHEN users interact with the system THEN their inputs SHALL be processed securely
7. WHEN errors occur THEN the system SHALL not expose sensitive information in error messages