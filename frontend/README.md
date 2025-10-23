# Credit Card Statement Parser - Frontend

A modern Next.js frontend application for the Credit Card Statement Parser API. Upload credit card statements and extract key information with confidence scores.

## Features

- 📤 **Drag & Drop Upload**: Simple file upload interface with drag-and-drop support
- 🎯 **Real-time Processing**: Automatic polling for job completion
- 📊 **Confidence Scores**: Visual indicators for extraction accuracy
- 🏦 **Multi-Bank Support**: Kotak, HDFC, ICICI, American Express, Capital One
- 🎨 **Modern UI**: Beautiful, responsive design with Tailwind CSS
- ⚡ **Fast**: Built with Next.js 14 and App Router

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client for API calls
- **React Dropzone** - File upload component
- **Lucide React** - Beautiful icons

## Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running on `http://localhost:8000` (see main README)

## Getting Started

### 1. Install Dependencies

```bash
npm install
# or
yarn install
```

### 2. Configure Environment

Create a `.env.local` file (already provided):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 4. Build for Production

```bash
npm run build
npm start
# or
yarn build
yarn start
```

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout with metadata
│   ├── page.tsx            # Main page component
│   └── globals.css         # Global styles
├── components/
│   ├── Header.tsx          # Header component
│   ├── FileUpload.tsx      # File upload with drag-drop
│   └── ResultsDisplay.tsx  # Results visualization
├── lib/
│   └── api.ts              # API service layer
├── types/
│   └── index.ts            # TypeScript type definitions
├── public/                 # Static assets
├── .env.local              # Environment variables
├── next.config.js          # Next.js configuration
├── tailwind.config.js      # Tailwind CSS configuration
├── tsconfig.json           # TypeScript configuration
└── package.json            # Dependencies
```

## Usage

### Upload a Statement

1. **Drag and drop** a PDF file or **click to browse**
2. Wait for the parsing to complete (usually 2-5 seconds)
3. View the extracted data with confidence scores

### Supported Banks

- ✅ Kotak Mahindra Bank
- ✅ HDFC Bank
- ✅ ICICI Bank
- ✅ American Express
- ✅ Capital One

### File Requirements

- **Format**: PDF only
- **Size**: Maximum 10MB
- **Content**: Credit card statement from supported banks

## API Integration

The frontend communicates with the backend API:

- `POST /api/v1/parse/upload` - Upload statement
- `GET /api/v1/parse/status/{job_id}` - Get job status
- `GET /api/v1/parse/results/{job_id}` - Get parsing results
- `GET /api/v1/health` - Health check

All API calls include automatic error handling and retries.

## Components

### FileUpload

Handles file uploads with validation:
- Drag-and-drop support
- File type validation (PDF only)
- File size validation (10MB max)
- Visual feedback for drag states

### ResultsDisplay

Shows extracted data:
- Card number with masking
- Statement date
- Billing period (start/end)
- Total amount due
- Payment due date
- Confidence scores for each field
- Overall confidence percentage

### Header

Navigation and branding:
- Logo and app name
- Quick links to API docs
- Responsive design

## Development

### Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run ESLint
```

### Code Style

- TypeScript strict mode enabled
- ESLint with Next.js rules
- Prettier for code formatting

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

### Tailwind Configuration

Custom colors defined in `tailwind.config.js`:
- Primary: Blue (`#3B82F6`)
- Success: Green
- Warning: Yellow
- Error: Red

## Troubleshooting

### Backend Connection Error

Ensure the backend is running:
```bash
cd ..
docker-compose up
```

### Port Already in Use

Change the port:
```bash
PORT=3001 npm run dev
```

### Type Errors

Reinstall dependencies:
```bash
rm -rf node_modules package-lock.json
npm install
```

## Docker Deployment

Add the frontend to `docker-compose.yml`:

```yaml
frontend:
  build: ./frontend
  ports:
    - "3000:3000"
  environment:
    - NEXT_PUBLIC_API_URL=http://backend:8000
  depends_on:
    - backend
```

Create `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]
```

## Contributing

1. Follow the existing code style
2. Write meaningful commit messages
3. Test thoroughly before submitting
4. Update documentation as needed

## License

MIT License - see LICENSE file for details

## Support

For issues or questions:
- Check the [main README](../README.md)
- Review the [backend API docs](http://localhost:8000/docs)
- Open an issue on GitHub

## Links

- [Backend Repository](../)
- [API Documentation](http://localhost:8000/docs)
- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
