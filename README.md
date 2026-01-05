# Currency Converter App

A real-time web application for converting currencies and cryptocurrencies with instant results and trend visualization.

## Features
- Real-time currency conversion for 150+ currencies
- Cryptocurrency support (Bitcoin, Ethereum, etc.)
- Instant conversions using cached exchange rates
- Responsive design for desktop and mobile
- Trend graphs for market visualization

## Technologies Used
- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript
- **APIs**: Open Exchange Rates, CoinGecko
- **Libraries**: Flask-CORS, Requests

## Installation & Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/mudassar165/Currency_ConverterApp.git
   cd Currency_ConverterApp
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your browser and go to `http://127.0.0.1:5000`

## API Endpoints
- `GET /`: Serves the main application page
- `GET /api/init-data`: Fetches initial currency and crypto data
- `GET /api/convert?amount=100&from=USD&to=EUR`: Converts currency amounts

## Deployment

### Option 1: Deploy to Render (Free)
1. Create a free account at [Render](https://render.com)
2. Connect your GitHub repository
3. Create a new Web Service
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python app.py`
6. Add environment variable: `PORT=10000` (or any port)
7. Deploy!

### Option 2: Deploy to Heroku
1. Install Heroku CLI
2. Login: `heroku login`
3. Create app: `heroku create your-app-name`
4. Push to Heroku: `git push heroku main`
5. Open: `heroku open`

### Production Notes
- Set `DEBUG = False` in `config_api.py` for production
- Ensure API keys are secure (currently using free public APIs)
- The app uses free APIs with rate limits; consider upgrading for heavy usage

## Project Status
✅ **100% Complete**
- All errors fixed
- Performance optimized (instant conversions)
- Fully tested and functional
- Ready for deployment

## Usage
1. Select source and target currencies
2. Enter amount
3. View instant conversion result and trend graph
4. Switch between currencies and cryptocurrencies

## Troubleshooting
- If APIs fail, check network connection
- Ensure Python 3.8+ is installed
- For deployment issues, check logs in the hosting platform

## License
MIT License

## Author
Mudassar Nazar