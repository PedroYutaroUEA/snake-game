workspace "Snake Multiplayer Local" "Arquitetura baseada em Grid e Ticks para o Snake Multiplayer Local." {

    model {
        // --- NÍVEL 1: CONTEXTO ---
        players = person "Jogadores (1 a 4)" "Interagem com o jogo simultaneamente através de Teclados ou Joysticks (D-PAD e Analógicos)."

        snakeSystem = softwareSystem "Snake Multiplayer System" "Sistema de jogo cooperativo/competitivo local com simulação baseada em Malha (Grid)." {

            // --- NÍVEL 2: CONTAINERS ---
            assets = container "File System (Assets)" "Armazenamento local de efeitos sonoros rápidos (hit, eat)." "Diretório /assets" "Folder"

            app = container "Game Application" "Aplicação executável rodando a 60FPS, mas com física processada por Ticks." "Python 3 + Pygame CE" {

                // --- NÍVEL 3: COMPONENTES (CLIENT / INFRAESTRUTURA) ---
                gameClass = component "Game Orchestrator" "Gerencia o Game Loop (clock), delega o tempo (dt) e roteia cenas e áudio." "client/game.py"
                lobby = component "Lobby Scene" "Interface de conexão dinâmica, reserva de slots (P1-P4) e countdown." "client/lobby.py"
                inputMgr = component "Input Manager" "Roteador central de hardware. Detecta teclados/controles e previne conflitos de slots." "client/input/manager.py"
                profiles = component "Input Profiles" "Mapas estáticos (XBOX, PS) e funções geradoras de dicas de UI." "client/input/profiles.py"
                renderer = component "Renderer" "Desenha a malha geométrica, segmentos (draw_rect), overlays de UI e menus." "client/renderer.py"
                audioMgr = component "Audio Manager" "Gerenciador dinâmico de canais. Toca SFX baseados em eventos pontuais." "client/audio/manager.py"

                // --- NÍVEL 3: COMPONENTES (CORE / DOMÍNIO) ---
                sceneState = component "Scene State" "Enumeração do estado da Máquina (MENU, LOBBY, PLAY, GAME_OVER)." "core/scene.py"
                commands = component "Player Commands" "Dataclass de intenção puramente direcional (Up, Down, Left, Right)." "core/commands.py"
                world = component "World Engine" "Simulador por Ticks. Acumula o tempo e orquestra crescimentos, timers e spawns." "core/world.py"
                collisionMgr = component "Collision Manager" "Regras exatas de Grid: Head-to-Head, Body-Hit, PVP Kill e Paredes." "core/collisions.py"
                entities = component "Entities" "Objetos de domínio mutáveis (Snake com array de segmentos e timers, Food)." "core/entities/"
                utilsConfig = component "Config & Utils" "Parâmetros globais (GRID_SIZE, FPS) e abstrações visuais (draw_panel, draw_overlay)." "core/config.py / core/utils.py"

                // --- RELACIONAMENTOS ---

                // Máquina de Estados (Controle de Fluxo)
                gameClass -> sceneState "Lê e transita o estado principal"
                lobby -> sceneState "Informa quando a contagem regressiva acaba"
                renderer -> sceneState "Modifica a tela baseando-se no estado atual"

                // Orquestração de Telas & Input
                gameClass -> lobby "Delega a UI preparatória quando em LOBBY"
                lobby -> inputMgr "Obtém lista de IDs e tipos de hardwares conectados"
                lobby -> profiles "Solicita strings literais de botões para desenhar o Menu"
                renderer -> profiles "Solicita atalhos (Hints) para desenhar o Guia Principal"
                inputMgr -> profiles "Consulta as constantes estáticas de mapeamento SDL2"
                inputMgr -> commands "Gera e empacota intenções continuas por hardware"
                gameClass -> inputMgr "Coleta o Dict[PlayerCommand] via polling a 60FPS"

                // Atualização do Mundo (Ticks) e Domínio
                gameClass -> world "Injeta 'dt' e comandos capturados"
                world -> commands "Repassa a intenção registrada do jogador"
                world -> entities "Invoca step(), decrementa timers de invencibilidade e gera instâncias"
                world -> collisionMgr "Chama a detecção espacial estrita após executar o tick de movimento"
                entities -> commands "Snake intercepta o comando para impedir auto-colisão (Marcha-à-ré)"
                entities -> utilsConfig "Herda utilidades vetoriais essenciais e limites da grade"

                // Regras Espaciais
                collisionMgr -> entities "Verifica igualdade de coordenadas. Altera flags de vida e aplica Scores."
                collisionMgr -> utilsConfig "Usa wrap_pos ou is_out_of_bounds limitadores do mapa"

                // Saídas (Render e Áudio)
                gameClass -> renderer "Repassa leitura do estado atual (World/HUD)"
                gameClass -> audioMgr "Injeta eventos textuais capturados na simulação (ex: 'food_eaten_1')"
                renderer -> entities "Desempacota a lista de segmentos das Snakes para desenhar o corpo e fantasma"
                renderer -> utilsConfig "Chama funções de overlay e painéis translúcidos (draw_panel, draw_rect)"
            }
        }

        // --- RELACIONAMENTOS EXTERNOS ---
        players -> inputMgr "Enviam comandos direcionais brutos"
        players -> renderer "Visualizam grid, pontuações em tempo real e overlays"
        audioMgr -> assets "Carrega sons de mordidas e batidas em cache"
    }

    views {
        systemContext snakeSystem "Context" {
            include *
            autoLayout
        }

        container snakeSystem "Containers" {
            include *
            autoLayout
        }

        component app "Components" {
            include *
            autoLayout lr
            description "Diagrama C4 (Nível 3) detalhando a integração do Domínio (Ticks/Grid) com a Infraestrutura (Hardware/Pygame)."
        }

        styles {
            element "Person" {
              shape Person
              background #1a5632
              color #ffffff
            }
            element "Software System" {
              background #237841
              color #ffffff
            }
            element "Container" {
              background #2c9750
              color #ffffff
            }
            element "Component" {
              background #7ecb9a
              color #000000
            }
            element "Folder" {
              shape Folder
              background #fbbf24
              color #000000
            }
        }
    }

}
