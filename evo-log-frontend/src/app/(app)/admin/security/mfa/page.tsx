// src/app/(app)/admin/security/mfa/page.tsx - Security MFA Configuration - Fidèle 100% au HTML original
'use client'


import { TCodeSearch } from '@/components/ui/TCodeSearch'
export default function MfaConfigurationPage() {
  return (
    <>
      <style jsx global>{`
        .material-symbols-outlined {
          font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
        .material-symbols-outlined.fill {
          font-variation-settings: 'FILL 1';
        }
      `}</style>
      <div className="bg-surface-container-low text-on-surface font-body-md antialiased flex">
        
        

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col h-full overflow-hidden">
          
          

          
          <main className="flex-1 overflow-y-auto p-lg bg-surface-container-low">
            <div className="max-w-[1000px] mx-auto">
              {/* Breadcrumbs */}
              

              <div className="flex justify-between items-end mb-lg">
                <div>
                  <h2 className="font-headline-lg text-headline-lg text-on-surface">Multi-Factor Authentication</h2>
                  <p className="font-body-md text-body-md text-on-surface-variant mt-xxs">Secure your EVO-LOG ERP account with two-step verification.</p>
                </div>
                <div className="flex items-center gap-sm bg-surface-container-lowest px-md py-xs rounded border border-outline-variant">
                  <span className="material-symbols-outlined text-secondary fill text-[20px]">shield</span>
                  <span className="font-label-md text-label-md text-secondary">MFA Status: Inactive</span>
                </div>
              </div>

              {/* Bento Grid Layout */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-md">
                {/* QR Code Card */}
                <div className="md:col-span-1 bg-surface-container-lowest rounded-xl border border-outline-variant p-md flex flex-col shadow-sm">
                  <h3 className="font-title-md text-title-md text-on-surface mb-xs flex items-center gap-xs">
                    <span className="material-symbols-outlined text-primary">qr_code_scanner</span>
                    Authenticator App
                  </h3>
                  <p className="font-body-sm text-body-sm text-on-surface-variant mb-md">Scan this QR code with an authenticator app (like Google Authenticator or Authy).</p>
                  <div className="flex-1 flex flex-col items-center justify-center py-md">
                    <div className="bg-surface p-sm border border-outline-variant rounded mb-md">
                      <img alt="QR Code" className="w-[150px] h-[150px]" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAkXBjcz88_HCOHCxIuxpAXtI_VBcXT9f4zjKgRihqX9isb81cfBlETKK4CaL_ZpCL5VGF5JmMvcA1C4rV-aZozdOUF_y545_fQbryKK0GFGG2DITyPTp8KziM4kuC6adYValmNn_OD_Dw1g6O-DDbWbsBCu3Dm_YabO1jekbQ8JFduBEqcDaO2zn0LxFp_Fl2S_4kVElMgGgzXzvBWW2ydSTaO788CzE-lq8G473GKOtv1QPkxK-RZUDmojOW7rWp1xd82j6N1v4s"/>
                    </div>
                    <p className="font-label-sm text-label-sm text-on-surface-variant mb-xxs">Or enter this manual code:</p>
                    <code className="font-data-tabular text-data-tabular bg-surface-container px-sm py-xxs rounded text-on-surface border border-outline-variant select-all">JBSW Y3DP EHPK 3PXP</code>
                  </div>
                  <div className="mt-auto pt-md border-t border-outline-variant">
                    <label className="block font-label-md text-label-md text-on-surface mb-xs">Verification Code</label>
                    <div className="flex gap-xs">
                      <input className="flex-1 bg-surface border border-outline-variant rounded px-sm py-xs font-data-tabular text-data-tabular focus:ring-2 focus:ring-primary focus:outline-none text-center tracking-[0.2em]" placeholder="000 000" type="text"/>
                      <button className="bg-primary hover:bg-primary-fixed-dim text-on-primary rounded px-md py-xs font-label-md text-label-md transition-colors">Verify</button>
                    </div>
                  </div>
                </div>

                {/* Backup Codes Card */}
                <div className="md:col-span-2 bg-surface-container-lowest rounded-xl border border-outline-variant p-md flex flex-col shadow-sm relative overflow-hidden">
                  {/* Decorative gradient background subtle */}
                  <div className="absolute right-0 top-0 w-64 h-64 bg-primary/5 rounded-full blur-3xl -z-10 -translate-y-1/2 translate-x-1/3"></div>
                  <div className="flex justify-between items-start mb-md">
                    <div>
                      <h3 className="font-title-md text-title-md text-on-surface mb-xs flex items-center gap-xs">
                        <span className="material-symbols-outlined text-tertiary">key</span>
                        Backup Codes
                      </h3>
                      <p className="font-body-sm text-body-sm text-on-surface-variant">Save these single-use codes in a secure location. Use them to access your account if you lose your device.</p>
                    </div>
                    <button className="text-primary hover:text-primary-fixed-variant font-label-md text-label-md flex items-center gap-xs bg-primary/10 px-sm py-xs rounded transition-colors">
                      <span className="material-symbols-outlined text-[18px]">download</span>
                      Download TXT
                    </button>
                  </div>
                  <div className="bg-surface border border-outline-variant rounded-lg p-md mb-md flex-1">
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-y-sm gap-x-md">
                      <div className="font-data-tabular text-data-tabular text-on-surface flex items-center justify-between group">
                        <span>8472-9104</span>
                        <button className="opacity-0 group-hover:opacity-100 text-outline hover:text-primary transition-opacity"><span className="material-symbols-outlined text-[16px]">content_copy</span></button>
                      </div>
                      <div className="font-data-tabular text-data-tabular text-on-surface flex items-center justify-between group">
                        <span>3951-0284</span>
                        <button className="opacity-0 group-hover:opacity-100 text-outline hover:text-primary transition-opacity"><span className="material-symbols-outlined text-[16px]">content_copy</span></button>
                      </div>
                      <div className="font-data-tabular text-data-tabular text-on-surface flex items-center justify-between group">
                        <span>6105-8372</span>
                        <button className="opacity-0 group-hover:opacity-100 text-outline hover:text-primary transition-opacity"><span className="material-symbols-outlined text-[16px]">content_copy</span></button>
                      </div>
                      <div className="font-data-tabular text-data-tabular text-on-surface flex items-center justify-between group">
                        <span>9284-5710</span>
                        <button className="opacity-0 group-hover:opacity-100 text-outline hover:text-primary transition-opacity"><span className="material-symbols-outlined text-[16px]">content_copy</span></button>
                      </div>
                      <div className="font-data-tabular text-data-tabular text-on-surface flex items-center justify-between group">
                        <span>1048-2957</span>
                        <button className="opacity-0 group-hover:opacity-100 text-outline hover:text-primary transition-opacity"><span className="material-symbols-outlined text-[16px]">content_copy</span></button>
                      </div>
                      <div className="font-data-tabular text-data-tabular text-on-surface flex items-center justify-between group">
                        <span>7539-1826</span>
                        <button className="opacity-0 group-hover:opacity-100 text-outline hover:text-primary transition-opacity"><span className="material-symbols-outlined text-[16px]">content_copy</span></button>
                      </div>
                      <div className="font-data-tabular text-data-tabular text-on-surface flex items-center justify-between group">
                        <span>4820-9153</span>
                        <button className="opacity-0 group-hover:opacity-100 text-outline hover:text-primary transition-opacity"><span className="material-symbols-outlined text-[16px]">content_copy</span></button>
                      </div>
                      <div className="font-data-tabular text-data-tabular text-on-surface flex items-center justify-between group">
                        <span>2619-7485</span>
                        <button className="opacity-0 group-hover:opacity-100 text-outline hover:text-primary transition-opacity"><span className="material-symbols-outlined text-[16px]">content_copy</span></button>
                      </div>
                      <div className="font-data-tabular text-data-tabular text-on-surface flex items-center justify-between group">
                        <span className="line-through text-outline">5938-1024</span>
                        <span className="text-[10px] bg-outline-variant text-on-surface px-1 rounded ml-auto">USED</span>
                      </div>
                    </div>
                  </div>
                  <div className="mt-auto flex justify-end gap-sm border-t border-outline-variant pt-md">
                    <button className="text-on-surface-variant hover:text-on-surface font-label-md text-label-md px-md py-xs border border-outline-variant rounded transition-colors bg-surface-container-lowest">Print</button>
                    <button className="text-on-surface-variant hover:text-on-surface font-label-md text-label-md px-md py-xs border border-outline-variant rounded transition-colors bg-surface-container-lowest flex items-center gap-xs">
                      <span className="material-symbols-outlined text-[18px]">refresh</span>
                      Generate New Codes
                    </button>
                  </div>
                </div>

                {/* Security Preferences */}
                <div className="md:col-span-3 bg-surface-container-lowest rounded-xl border border-outline-variant p-md shadow-sm">
                  <h3 className="font-title-md text-title-md text-on-surface mb-md">Security Preferences</h3>
                  <div className="flex flex-col gap-sm">
                    <label className="flex items-start gap-md p-sm hover:bg-surface-container transition-colors rounded cursor-pointer border border-transparent hover:border-outline-variant">
                      <div className="relative inline-flex items-center cursor-pointer mt-1">
                        <input checked className="sr-only peer" type="checkbox" value=""/>
                        <div className="w-9 h-5 bg-outline-variant peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-primary"></div>
                      </div>
                      <div>
                        <div className="font-label-md text-label-md text-on-surface">Require MFA for T-Code execution</div>
                        <div className="font-body-sm text-body-sm text-on-surface-variant mt-xxs">Prompt for an authenticator code when executing high-risk transaction codes.</div>
                      </div>
                    </label>
                    <label className="flex items-start gap-md p-sm hover:bg-surface-container transition-colors rounded cursor-pointer border border-transparent hover:border-outline-variant">
                      <div className="relative inline-flex items-center cursor-pointer mt-1">
                        <input className="sr-only peer" type="checkbox" value=""/>
                        <div className="w-9 h-5 bg-outline-variant peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-primary"></div>
                      </div>
                      <div>
                        <div className="font-label-md text-label-md text-on-surface">Remember this device</div>
                        <div className="font-body-sm text-body-sm text-on-surface-variant mt-xxs">Skip MFA prompts on this browser for 30 days. Not recommended for shared computers.</div>
                      </div>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </main>
        </div>
      </div>
    </>
  )
}
