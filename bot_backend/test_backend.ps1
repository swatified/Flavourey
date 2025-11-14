# Test script for Flavourey Bot Backend

Write-Host "🧪 Testing Flavourey Bot Backend" -ForegroundColor Green
Write-Host ""

# Check if server is running
Write-Host "1. Checking if server is running at http://localhost:8000..." -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/" -Method GET -UseBasicParsing
    Write-Host "   ✅ Server is running!" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "   ❌ Server is not running. Please start it first:" -ForegroundColor Red
    Write-Host "      cd bot_backend" -ForegroundColor Yellow
    Write-Host "      .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "      uvicorn src.server:app --reload --port 8000" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Test non-streaming chat completions
Write-Host "2. Testing /chat/completions (non-streaming)..." -ForegroundColor Cyan

$body = @{
    model = "gemini-2.5-pro"
    messages = @(
        @{
            role = "user"
            content = "Hi! Can you help me with food recommendations?"
        }
    )
    stream = $false
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/chat/completions" `
        -Method POST `
        -Body $body `
        -ContentType "application/json" `
        -UseBasicParsing
    
    $json = $response.Content | ConvertFrom-Json
    Write-Host "   ✅ Response received!" -ForegroundColor Green
    Write-Host "   Model: $($json.model)" -ForegroundColor Gray
    Write-Host "   Reply: $($json.choices[0].message.content.Substring(0, [Math]::Min(100, $json.choices[0].message.content.Length)))..." -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# Test with tools
Write-Host "3. Testing /chat/completions with search_menu tool..." -ForegroundColor Cyan

$bodyWithTools = @{
    model = "gemini-2.5-pro"
    messages = @(
        @{
            role = "user"
            content = "I feel stressed, recommend comfort food under 300 rupees"
        }
    )
    tools = @(
        @{
            type = "function"
            function = @{
                name = "search_menu"
                description = "Search menu items based on mood and constraints"
                parameters = @{
                    type = "object"
                    properties = @{
                        mood = @{
                            type = "string"
                            description = "User's current mood"
                        }
                        max_budget = @{
                            type = "number"
                            description = "Maximum budget in INR"
                        }
                        dietary = @{
                            type = "string"
                            enum = @("veg", "non-veg", "vegan", "any")
                        }
                        allergens_to_avoid = @{
                            type = "array"
                            items = @{
                                type = "string"
                            }
                        }
                    }
                }
            }
        }
    )
    stream = $false
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/chat/completions" `
        -Method POST `
        -Body $bodyWithTools `
        -ContentType "application/json" `
        -UseBasicParsing
    
    $json = $response.Content | ConvertFrom-Json
    Write-Host "   ✅ Tool calling works!" -ForegroundColor Green
    Write-Host "   Reply: $($json.choices[0].message.content.Substring(0, [Math]::Min(150, $json.choices[0].message.content.Length)))..." -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# Test legacy endpoint
Write-Host "4. Testing legacy /api/ask endpoint..." -ForegroundColor Cyan

$legacyBody = @{
    session_id = "test_session_001"
    message = "I feel happy!"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/ask" `
        -Method POST `
        -Body $legacyBody `
        -ContentType "application/json" `
        -UseBasicParsing
    
    $json = $response.Content | ConvertFrom-Json
    Write-Host "   ✅ Legacy endpoint works!" -ForegroundColor Green
    Write-Host "   Reply: $($json.reply)" -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

Write-Host "✨ Testing complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📚 For more tests, see:" -ForegroundColor Cyan
Write-Host "   - bot_backend/README.md" -ForegroundColor Yellow
Write-Host "   - bot_backend/IMPLEMENTATION.md" -ForegroundColor Yellow
Write-Host ""
Write-Host "🚀 To test streaming, use curl:" -ForegroundColor Cyan
Write-Host '   curl -X POST http://localhost:8000/chat/completions -H "Content-Type: application/json" -d "{\"model\":\"gemini-2.5-pro\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello!\"}],\"stream\":true}"' -ForegroundColor Yellow
Write-Host ""
