# Weather & Outdoor Activity Emailer 🌤️

An automated system that fetches weather forecasts and suggests personalized outdoor activities, delivered straight to your inbox.

## 🌟 Features

- 🌡️ Fetches tomorrow's detailed weather forecast
- 🎯 Generates AI-powered outdoor activity suggestions
- 📧 Delivers personalized email reports
- 🤖 Powered by Groq Cloud's `llama-3.3-70b-versatile` model

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- API keys for:
  - Resend
  - RapidAPI (WeatherAPI)
  - Groq Cloud

### Installation

1. **Clone the Repository**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-directory>
   ```

2. **Set Up Virtual Environment**
   ```bash
   python -m venv venv
   
   # On Linux/MacOS
   source venv/bin/activate
   
   # On Windows
   venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following:

```env
# Email Configuration (Resend)
RESEND_API_KEY=your_resend_api_key
FROM_EMAIL=your_email@example.com
TO_EMAIL=recipient_email@example.com

# Weather Data (RapidAPI)
RAPIDAPI_KEY=your_rapidapi_key

# AI Suggestions (Groq)
GROQ_API_KEY=your_groq_api_key

# Location Settings
LOCATION=City, State  # Example: Houston, Texas
```

## 📧 Sample Email Output

**Subject:** Tomorrow's Weather & Outdoor Activities 🌤️ - Houston, Texas

```html
<h2>Tomorrow's Weather in Houston, Texas (2025-01-05)</h2>
<p><strong>Condition:</strong> Clear sky</p>
<p><strong>Average Temperature:</strong> 22°C / 71.6°F</p>
<p><strong>Max Wind Speed:</strong> 10 kph</p>
<p><strong>Humidity:</strong> 60%</p>

<h3>Suggested Outdoor Activities</h3>
<ul>
    <li>Go for a morning jog by the lake.</li>
    <li>Plan an outdoor lunch with friends at the park.</li>
    <li>Enjoy a sunset bike ride along scenic trails.</li>
</ul>
```

## 🛠️ Technical Details

### Dependencies

- `resend`: Email delivery
- `http.client`: Weather API integration
- `python-dotenv`: Environment management
- `groq`: AI-powered suggestions
- `logging`: Error tracking

### API Setup Guide

1. **Resend API**
   - Sign up at [Resend](https://resend.com)
   - Generate API key
   - Add to `.env`

2. **RapidAPI (WeatherAPI)**
   - Join [RapidAPI](https://rapidapi.com)
   - Subscribe to WeatherAPI
   - Copy API key to `.env`

3. **Groq Cloud**
   - Register for [Groq Cloud](https://groq.com)
   - Get API access
   - Configure in `.env`

## 🔍 Troubleshooting

Common issues and solutions:

- **Missing Environment Variables**: Verify `.env` file configuration
- **WeatherAPI Errors**: Check API quota and location format
- **Groq Cloud Issues**: Validate API key and model access

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Submit pull requests
- Report issues
- Suggest improvements

## 📄 License

This project is licensed under the MIT License.

## 📬 Contact

Questions or support? Reach out at vinoddevopscloud99@gmail.com

---
