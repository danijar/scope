import { spawn } from 'node:child_process'
import { parseArgs } from 'node:util'

const { values } = parseArgs({ options: {
  basedir: { type: 'string' },
  port: { type: 'string' },
} })

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
