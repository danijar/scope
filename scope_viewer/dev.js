import { spawn, spawnSync } from 'node:child_process'
import { existsSync } from 'node:fs'
import { parseArgs } from 'node:util'

if (!existsSync(new URL('node_modules', import.meta.url)))
  spawnSync('npm', ['install'], { stdio: 'inherit' })
if (!existsSync(new URL('dist', import.meta.url)))
  spawnSync('npm', ['run', 'build'], { stdio: 'inherit' })

const { values } = parseArgs({ options: {
  basedir: { type: 'string' },
  port: { type: 'string' },
} })
values.basedir ??= process.env.npm_config_basedir
values.port ??= process.env.npm_config_port

const env = { ...process.env }
if (values.basedir)
  env.SCOPE_BASEDIR = values.basedir
const viteArgs = values.port ? ['--port', values.port] : []

const procs = [
  spawn('npm', ['run', 'frontend', '--', ...viteArgs], { stdio: 'inherit', env }),
  spawn('npm', ['run', 'backend'], { stdio: 'inherit', env }),
]
for (const proc of procs) {
  proc.on('exit', code => {
    process.exitCode = code
    for (const other of procs)
      other.kill()
  })
}
