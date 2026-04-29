import { NextResponse, type NextRequest } from "next/server";

/**
 * 1) HTTP Basic Auth — BASIC_AUTH_USER / BASIC_AUTH_PASS 환경변수가 설정되면 활성화.
 *    Vercel 에서 env var 설정한 경우에만 잠금. 로컬 dev 에서는 설정 안 하면 자동으로 off.
 * 2) Server Components 가 현재 pathname 을 읽을 수 있도록 request 헤더에 주입.
 */
export function middleware(req: NextRequest) {
  const user = process.env.BASIC_AUTH_USER;
  const pass = process.env.BASIC_AUTH_PASS;

  if (user && pass) {
    const auth = req.headers.get("authorization");
    if (!auth || !auth.startsWith("Basic ")) {
      return new NextResponse("인증이 필요합니다", {
        status: 401,
        headers: {
          "WWW-Authenticate": 'Basic realm="GEO Dashboard", charset="UTF-8"',
        },
      });
    }
    const decoded = atob(auth.slice(6));
    const idx = decoded.indexOf(":");
    const providedUser = idx >= 0 ? decoded.slice(0, idx) : "";
    const providedPass = idx >= 0 ? decoded.slice(idx + 1) : "";
    if (providedUser !== user || providedPass !== pass) {
      return new NextResponse("잘못된 자격증명", {
        status: 401,
        headers: {
          "WWW-Authenticate": 'Basic realm="GEO Dashboard", charset="UTF-8"',
        },
      });
    }
  }

  const requestHeaders = new Headers(req.headers);
  requestHeaders.set("x-pathname", req.nextUrl.pathname);
  return NextResponse.next({
    request: { headers: requestHeaders },
  });
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|api).*)"],
};
