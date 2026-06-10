export type PermissionSet = {
  modules: string[]
  kpis: string[]
}

export type AuthUser = {
  id: string
  name: string
  username: string
  roles: string[]
  permissions: PermissionSet
  base_id?: string | null
}

export type AuthCompany = {
  id: string
  name: string
  token: string
  bases: Array<{
    id: string
    name: string
    alias?: string | null
    host?: string | null
    port?: number | null
    charset?: string | null
    status?: string | null
  }>
}
