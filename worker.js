export default {
  async fetch(request) {
    const url = new URL(request.url);
    const targetUrl = url.searchParams.get('url');

    if (!targetUrl) {
      return new Response('Missing url parameter', { status: 400 });
    }

    // Only allow Yahoo Finance domains
    const allowed = ['query1.finance.yahoo.com', 'query2.finance.yahoo.com'];
    const targetHost = new URL(targetUrl).hostname;
    if (!allowed.includes(targetHost)) {
      return new Response('Domain not allowed', { status: 403 });
    }

    const response = await fetch(targetUrl);
    const data = await response.text();

    return new Response(data, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json',
      },
    });
  },
};
