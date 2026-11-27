import { useEffect, useState } from 'react';
import { ChevronDown, Menu, X } from 'lucide-react';

const VIDEO_URL =
  'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260803_192301_9231ed6b-c55c-4a48-909c-4ebe11cf2e11.mp4';

const LOGO_PATH =
  'M 128 128 C 128 198.692 70.692 256 0 256 C 0 185.308 57.308 128 128 128 Z M 128 128 C 198.692 128 256 185.308 256 256 C 185.308 256 128 198.692 128 128 Z M 0 0 C 70.692 0 128 57.308 128 128 C 57.308 128 0 70.692 0 0 Z M 256 0 C 256 70.692 198.692 128 128 128 C 128 57.308 185.308 0 256 0 Z';

const CTA_GRADIENT = { background: 'linear-gradient(to bottom, #2B2B2B, #101010)' };

const NAV_LINKS = [
  { label: 'Modules' },
  { label: 'Clientele' },
  { label: 'Solutions', dropdown: true },
  { label: 'Billing' },
];

function Logo() {
  return (
    <a href="#" className="flex items-center gap-2">
      <svg width="24" height="24" viewBox="0 0 256 256" className="fill-[#010101] lg:fill-white" aria-hidden="true">
        <path d={LOGO_PATH} />
      </svg>
      <span className="text-lg font-semibold text-[#010101] lg:text-white">nexum</span>
    </a>
  );
}

export default function Hero() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    document.body.style.overflow = open ? 'hidden' : '';
    return () => {
      document.body.style.overflow = '';
    };
  }, [open]);

  return (
    <section className="relative h-screen w-full overflow-hidden">
      <video
        className="absolute inset-0 h-full w-full object-cover"
        src={VIDEO_URL}
        autoPlay
        loop
        muted
        playsInline
      />

      <div className="relative z-10 flex h-full flex-col">
        {/* Top bar */}
        <nav className="flex items-center justify-between px-5 py-5 sm:px-8 sm:py-6 lg:px-12">
          <Logo />

          <div className="hidden items-center gap-3 md:flex">
            <div className="flex items-center gap-1 rounded-full bg-white/10 px-1.5 py-1.5 backdrop-blur-lg">
              {NAV_LINKS.map((link) => (
                <a
                  key={link.label}
                  href="#"
                  className="flex items-center gap-1 rounded-full px-4 py-1.5 text-sm font-medium text-white/80 transition-colors hover:bg-white/10 hover:text-white"
                >
                  {link.label}
                  {link.dropdown && <ChevronDown className="h-3.5 w-3.5" />}
                </a>
              ))}
            </div>
            <a
              href="#"
              className="flex items-center self-stretch rounded-full px-5 text-sm font-medium text-white transition-opacity hover:opacity-90"
              style={CTA_GRADIENT}
            >
              Get started
            </a>
          </div>

          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            aria-label={open ? 'Close menu' : 'Open menu'}
            aria-expanded={open}
            className="relative z-50 flex h-10 w-10 items-center justify-center rounded-full bg-white/10 backdrop-blur-lg md:hidden"
          >
            <Menu
              className={`absolute h-5 w-5 text-[#010101] transition-all duration-300 lg:text-white ${
                open ? 'rotate-90 scale-0 opacity-0' : 'rotate-0 scale-100 opacity-100'
              }`}
            />
            <X
              className={`absolute h-5 w-5 text-[#010101] transition-all duration-300 lg:text-white ${
                open ? 'rotate-0 scale-100 opacity-100' : '-rotate-90 scale-0 opacity-0'
              }`}
            />
          </button>
        </nav>

        {/* Mobile overlay */}
        <div
          onClick={() => setOpen(false)}
          className={`fixed inset-0 z-40 bg-black/80 backdrop-blur-md transition-opacity duration-300 md:hidden ${
            open ? 'opacity-100' : 'pointer-events-none opacity-0'
          }`}
        />

        {/* Mobile drawer */}
        <aside
          className={`fixed right-0 top-0 z-40 flex h-full w-72 flex-col bg-black/90 backdrop-blur-xl transition-transform duration-500 ease-[cubic-bezier(0.16,1,0.3,1)] md:hidden ${
            open ? 'translate-x-0' : 'translate-x-full'
          }`}
          aria-hidden={!open}
        >
          <div className="flex flex-col gap-2 px-6 pt-24">
            {NAV_LINKS.map((link, index) => (
              <a
                key={link.label}
                href="#"
                onClick={() => setOpen(false)}
                className="flex items-center justify-between rounded-xl px-4 py-3.5 text-base font-medium text-white/80 hover:bg-white/10 hover:text-white"
                style={{
                  opacity: open ? 1 : 0,
                  transform: open ? 'translateX(0)' : 'translateX(24px)',
                  transition: 'opacity 400ms ease, transform 400ms ease, background-color 150ms, color 150ms',
                  transitionDelay: open ? `${(index + 1) * 60}ms` : '0ms',
                }}
              >
                {link.label}
                {link.dropdown && <ChevronDown className="h-4 w-4" />}
              </a>
            ))}
          </div>
          <div
            className="mt-auto px-6 pb-10"
            style={{
              opacity: open ? 1 : 0,
              transform: open ? 'translateY(0)' : 'translateY(16px)',
              transition: 'opacity 400ms ease, transform 400ms ease',
              transitionDelay: open ? '300ms' : '0ms',
            }}
          >
            <a
              href="#"
              className="block w-full rounded-full px-6 py-3 text-center text-sm font-medium text-white transition-opacity hover:opacity-90"
              style={CTA_GRADIENT}
            >
              Get started
            </a>
          </div>
        </aside>

        {/* Bottom-anchored content */}
        <div className="mt-auto flex flex-col gap-6 px-5 pb-8 sm:gap-8 sm:px-8 sm:pb-12 lg:flex-row lg:items-end lg:justify-between lg:px-12 lg:pb-16">
          <div className="max-w-xl">
            <h1 className="text-3xl font-semibold leading-[1.1] tracking-tight text-[#010101] sm:text-4xl lg:text-[3.5rem] lg:text-white">
              Ship AI workers that grind while you rest
            </h1>
            <form
              onSubmit={(e) => e.preventDefault()}
              className="mt-6 flex flex-col gap-3 sm:mt-8 sm:inline-flex sm:flex-row sm:items-center sm:gap-0 sm:rounded-full sm:bg-white sm:p-1.5"
            >
              <input
                type="email"
                placeholder="Type your email"
                aria-label="Email"
                className="rounded-full bg-white px-5 py-3 text-sm text-gray-900 placeholder-gray-400 outline-none sm:w-64 sm:rounded-none sm:bg-transparent sm:px-4 sm:py-2"
              />
              <button
                type="submit"
                className="rounded-full px-6 py-3 text-sm font-medium text-white transition-opacity hover:opacity-90 sm:py-2.5"
                style={CTA_GRADIENT}
              >
                Get started
              </button>
            </form>
          </div>

          <div className="flex w-full flex-col gap-4 sm:flex-row lg:w-auto lg:gap-5">
            <div className="flex flex-col justify-between rounded-2xl bg-white/10 p-5 backdrop-blur-lg sm:w-64 sm:p-6">
              <div
                className="text-3xl font-normal tracking-tight text-[#010101] sm:text-4xl lg:text-white"
                style={{ fontFamily: "'Silkscreen', cursive" }}
              >
                42,500+
              </div>
              <p className="mt-3 text-sm leading-relaxed text-[#010101]/70 sm:mt-4 lg:text-white/70">
                Teams run Nexum to handle recurring ops daily.
              </p>
            </div>

            <div className="rounded-2xl bg-white/10 p-5 backdrop-blur-lg sm:w-64 sm:p-6">
              <div className="mb-3 flex items-center gap-2 sm:mb-4">
                <div className="flex h-6 w-6 items-center justify-center rounded-md bg-black text-xs font-bold text-white">S</div>
                <span className="text-sm font-semibold text-[#010101] lg:text-white">Stratify</span>
              </div>
              <p className="text-sm leading-relaxed text-[#010101]/80 lg:text-white/80">
                "With Nexum we went from managing tedious operational work to having AI agents that handle everything."
              </p>
              <div className="mt-4 flex items-center gap-3 sm:mt-5">
                <img
                  src="https://i.pravatar.cc/72?img=12"
                  alt="Sara Klein"
                  className="h-9 w-9 rounded-full bg-white/20 object-cover"
                />
                <div>
                  <div className="text-sm font-semibold text-[#010101] lg:text-white">Sara Klein</div>
                  <div className="text-xs text-[#010101]/60 lg:text-white/60">Dir of Operations</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
