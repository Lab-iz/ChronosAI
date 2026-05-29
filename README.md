# CHRONOS-SEGURO

CHRONOS-SEGURO e uma plataforma de simulacao orbital hibrida. O sistema combina motor fisico rapido, correcao por IA residual, guarda de seguranca e recuo fisico para manter estabilidade e clareza cientifica.

## Execucao Rapida

```powershell
python run.py
```

Depois acesse:

```text
http://127.0.0.1:8000/
```

## Instalacao

```powershell
python -m pip install -e ".[ml,science,dev]"
```

Opcionalmente, para usar REBOUND:

```powershell
python -m pip install -r requisitos-rebound.txt
```

## CLI

```powershell
chronos gerar-generalista
chronos gerar-especialista
chronos treinar-generalista
chronos treinar-especialista
chronos simular
chronos validar-apophis
```

Se `chronos` nao estiver no PATH:

```powershell
python -m chronos_seguro.aplicativos.linha_comando.principal <comando>
```

## Documentacao

- [Como rodar](documentacao/como_rodar.md)
- [Deploy no Render](documentacao/deploy_render.md)
- [Arquitetura](documentacao/arquitetura.md)
- [Metodologia](documentacao/metodologia.md)
- [Protocolo Apophis](documentacao/protocolo_apophis.md)
