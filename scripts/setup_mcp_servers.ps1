param(
    [Parameter(Mandatory=$false)]
    [string]$Context7Key = $env:CONTEXT7_API_KEY,
    
    [Parameter(Mandatory=$false)]
    [string]$GitHubToken = $env:GITHUB_TOKEN,
    
    [Parameter(Mandatory=$false)]
    [switch]$Force = $false
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "🔧 $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️ $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

# MCP configuration directory
$mcpConfigDir = "$env:APPDATA\Cursor\User\globalStorage\rooveterinaryinc.cursor-mcp"
$mcpConfigFile = "$mcpConfigDir\servers.json"

Write-Step "Setting up MCP servers for Cursor..."

# Create MCP config directory if it doesn't exist
if (-not (Test-Path $mcpConfigDir)) {
    New-Item -ItemType Directory -Force -Path $mcpConfigDir | Out-Null
    Write-Step "Created MCP config directory: $mcpConfigDir"
}

# MCP server configurations
$mcpServers = @{
    "context7" = @{
        "command" = "node"
        "args" = @("C:\Users\%USERNAME%\AppData\Roaming\npm\node_modules\@context7\mcp-server\dist\index.js")
        "env" = @{
            "CONTEXT7_API_KEY" = $Context7Key
        }
        "description" = "Context7 MCP Server for code intelligence"
    }
    
    "github" = @{
        "command" = "docker"
        "args" = @("run", "-i", "--rm", "-e", "GITHUB_TOKEN=$GitHubToken", "mcp/github")
        "env" = @{
            "GITHUB_TOKEN" = $GitHubToken  
        }
        "description" = "GitHub MCP Server"
    }
    
    "filesystem" = @{
        "command" = "npx"
        "args" = @("-y", "@modelcontextprotocol/server-filesystem", ".")
        "description" = "Filesystem MCP Server"
    }
    
    "sqlite" = @{
        "command" = "npx"
        "args" = @("-y", "@modelcontextprotocol/server-sqlite")
        "description" = "SQLite MCP Server"  
    }
    
    "memory" = @{
        "command" = "npx"
        "args" = @("-y", "@modelcontextprotocol/server-memory")
        "description" = "Memory MCP Server"
    }
}

# Check if config exists and handle overwrite
if (Test-Path $mcpConfigFile -and -not $Force) {
    Write-Warning "MCP configuration already exists: $mcpConfigFile"
    $response = Read-Host "Overwrite existing configuration? (y/n)"
    if ($response -ne "y") {
        Write-Step "Keeping existing configuration. Use -Force to overwrite."
        exit 0
    }
}

try {
    # Create MCP configuration
    $mcpConfig = @{
        "mcpServers" = $mcpServers
    }
    
    # Convert to JSON and save
    $jsonConfig = $mcpConfig | ConvertTo-Json -Depth 10
    $jsonConfig | Out-File -FilePath $mcpConfigFile -Encoding UTF8
    
    Write-Success "MCP configuration created: $mcpConfigFile"
    
    # Validate configuration
    Write-Step "Validating MCP configuration..."
    
    if (Test-Path "scripts\validate_mcp_configs.py") {
        python scripts\validate_mcp_configs.py
    }
    
    # Install Context7 MCP server if needed
    Write-Step "Installing Context7 MCP server via npm..."
    try {
        npm install -g @context7/mcp-server
        Write-Success "Context7 MCP server installed"
    } catch {
        Write-Warning "Failed to install Context7 MCP server via npm: $($_.Exception.Message)"
    }
    
    # Check Docker for GitHub MCP
    Write-Step "Checking Docker for GitHub MCP server..."
    try {
        $dockerVersion = docker --version
        Write-Success "Docker is available: $dockerVersion"
        
        # Pull GitHub MCP image
        docker pull mcp/github
        Write-Success "GitHub MCP Docker image pulled"
    } catch {
        Write-Warning "Docker not available for GitHub MCP server: $($_.Exception.Message)"
    }
    
    Write-Success "MCP servers setup completed!"
    Write-Step "Next steps:"
    Write-Host "1. Restart Cursor completely" -ForegroundColor White
    Write-Host "2. Wait 1-2 minutes for MCP servers to initialize" -ForegroundColor White  
    Write-Host "3. Open a new chat and test MCP functionality" -ForegroundColor White
    Write-Host "4. Run: python scripts\check_mcp_setup.py" -ForegroundColor White
    
} catch {
    Write-Error "Failed to setup MCP servers: $($_.Exception.Message)"
    exit 1
}