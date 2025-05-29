# Script para publicar o projeto JSON Converter no Git

# Verifica se o Git está instalado
function Test-GitInstalled {
    try {
        $gitVersion = git --version
        Write-Host "Git instalado: $gitVersion" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "Git não está instalado ou não está no PATH. Por favor, instale o Git antes de continuar." -ForegroundColor Red
        Write-Host "Você pode baixá-lo em: https://git-scm.com/downloads" -ForegroundColor Yellow
        return $false
    }
}

# Verifica se o diretório atual é um repositório Git
function Test-GitRepository {
    if (Test-Path -Path ".git" -PathType Container) {
        Write-Host "Repositório Git já inicializado." -ForegroundColor Green
        return $true
    } else {
        Write-Host "Este diretório não é um repositório Git." -ForegroundColor Yellow
        return $false
    }
}

# Inicializa um novo repositório Git
function Initialize-GitRepository {
    Write-Host "Inicializando novo repositório Git..." -ForegroundColor Cyan
    git init
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Repositório Git inicializado com sucesso!" -ForegroundColor Green
        return $true
    } else {
        Write-Host "Falha ao inicializar o repositório Git." -ForegroundColor Red
        return $false
    }
}

# Adiciona arquivos ao Git
function Add-GitFiles {
    Write-Host "Adicionando arquivos ao Git..." -ForegroundColor Cyan
    git add .
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Arquivos adicionados com sucesso!" -ForegroundColor Green
        return $true
    } else {
        Write-Host "Falha ao adicionar arquivos." -ForegroundColor Red
        return $false
    }
}

# Cria um commit
function New-GitCommit {
    param (
        [string]$Message = "Atualização do projeto JSON Converter"
    )
    
    Write-Host "Criando commit com a mensagem: '$Message'..." -ForegroundColor Cyan
    git commit -m $Message
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Commit criado com sucesso!" -ForegroundColor Green
        return $true
    } else {
        Write-Host "Falha ao criar commit. Verifique se há alterações para commitar." -ForegroundColor Red
        return $false
    }
}

# Configura o repositório remoto
function Set-GitRemote {
    param (
        [string]$RemoteName = "origin",
        [string]$RemoteUrl
    )
    
    # Verifica se o remote já existe
    $remoteExists = git remote | Where-Object { $_ -eq $RemoteName }
    
    if ($remoteExists) {
        Write-Host "Atualizando URL do repositório remoto '$RemoteName'..." -ForegroundColor Cyan
        git remote set-url $RemoteName $RemoteUrl
    } else {
        Write-Host "Adicionando repositório remoto '$RemoteName'..." -ForegroundColor Cyan
        git remote add $RemoteName $RemoteUrl
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Repositório remoto configurado com sucesso!" -ForegroundColor Green
        return $true
    } else {
        Write-Host "Falha ao configurar repositório remoto." -ForegroundColor Red
        return $false
    }
}

# Envia alterações para o repositório remoto
function Push-GitChanges {
    param (
        [string]$RemoteName = "origin",
        [string]$Branch = "main"
    )
    
    Write-Host "Enviando alterações para o repositório remoto ($RemoteName/$Branch)..." -ForegroundColor Cyan
    git push -u $RemoteName $Branch
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Alterações enviadas com sucesso!" -ForegroundColor Green
        return $true
    } else {
        Write-Host "Falha ao enviar alterações. Verifique suas credenciais e conexão." -ForegroundColor Red
        return $false
    }
}

# Função principal
function Publish-ToGit {
    param (
        [string]$CommitMessage,
        [string]$RemoteUrl,
        [string]$Branch = "main"
    )
    
    # Verifica se o Git está instalado
    if (-not (Test-GitInstalled)) {
        return
    }
    
    # Verifica se é um repositório Git ou inicializa um novo
    if (-not (Test-GitRepository)) {
        if (-not (Initialize-GitRepository)) {
            return
        }
    }
    
    # Adiciona arquivos
    if (-not (Add-GitFiles)) {
        return
    }
    
    # Cria commit
    if ([string]::IsNullOrEmpty($CommitMessage)) {
        $CommitMessage = Read-Host "Digite a mensagem do commit"
    }
    if (-not (New-GitCommit -Message $CommitMessage)) {
        return
    }
    
    # Configura repositório remoto se fornecido
    if (-not [string]::IsNullOrEmpty($RemoteUrl)) {
        if (-not (Set-GitRemote -RemoteUrl $RemoteUrl)) {
            return
        }
        
        # Envia alterações
        if (-not (Push-GitChanges -Branch $Branch)) {
            return
        }
    } else {
        Write-Host "URL do repositório remoto não fornecida. Pulando o envio das alterações." -ForegroundColor Yellow
        Write-Host "Para enviar as alterações posteriormente, execute:" -ForegroundColor Yellow
        Write-Host "git remote add origin <URL_DO_REPOSITORIO>" -ForegroundColor Yellow
        Write-Host "git push -u origin $Branch" -ForegroundColor Yellow
    }
    
    Write-Host "\nProcesso de publicação concluído!" -ForegroundColor Green
}

# Execução principal do script
Write-Host "=== Publicação do Projeto JSON Converter no Git ===" -ForegroundColor Cyan

# Solicita informações ao usuário se não fornecidas como parâmetros
$commitMessage = Read-Host "Digite a mensagem do commit (ou pressione Enter para usar a mensagem padrão)"
if ([string]::IsNullOrEmpty($commitMessage)) {
    $commitMessage = "Atualização do projeto JSON Converter"
}

$remoteUrl = Read-Host "Digite a URL do repositório remoto (ou pressione Enter para pular)"

$branch = Read-Host "Digite o nome do branch (ou pressione Enter para usar 'main')"
if ([string]::IsNullOrEmpty($branch)) {
    $branch = "main"
}

# Executa a função principal
Publish-ToGit -CommitMessage $commitMessage -RemoteUrl $remoteUrl -Branch $branch