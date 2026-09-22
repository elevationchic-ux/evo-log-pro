import loginPanelSvg from '@/app/login-panel.svg'

export function AuthLeftPanel() {
  return (
    <div
      className="hidden lg:flex lg:w-[55%] h-screen overflow-hidden"
      style={{ backgroundColor: '#0A1628' }}
    >
      {/* ── SVG Panel ── */}
      <div className="w-full h-full flex items-center justify-center">
        <img
          src={loginPanelSvg.src}
          alt="EVO-LOG SaaS - Port Autonome de Douala"
          className="w-full h-full object-cover"
        />
      </div>
    </div>
  )
}
