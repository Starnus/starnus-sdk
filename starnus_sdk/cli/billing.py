"""
starnus billing — manage subscriptions and credits
"""

import webbrowser

import click

from starnus_sdk.cli.main import pass_client, _fmt_date


@click.group(name="billing")
def billing_group():
    """Manage your Starnus subscription and credits."""


@billing_group.command("status")
@pass_client
def status_cmd(client):
    """Show current plan, credits, and subscription status."""
    b = client.billing.balance()
    click.echo(f"Tier:               {b.tier or 'N/A'}")
    click.echo(f"Subscription:       {b.subscription_status or 'N/A'}")
    remaining = b.credits_remaining if b.credits_remaining is not None else "N/A"
    limit = b.credits_limit if b.credits_limit is not None else "N/A"
    click.echo(f"Credits remaining:  {remaining} / {limit}")


@billing_group.command("plans")
@click.option("--currency", default="eur", show_default=True, help="Currency (eur, usd).")
@pass_client
def plans_cmd(client, currency: str):
    """List available subscription plans."""
    plans = client.billing.plans(currency=currency.lower())
    if not plans:
        click.echo("No plans available.")
        return
    click.echo(f"{'NAME':<15} {'SLUG':<12} {'PRICE':<10} {'INTERVAL':<10} CURRENCY")
    click.echo("-" * 60)
    for p in plans:
        click.echo(f"{p.name:<15} {p.slug:<12} {p.price:<10} {p.interval:<10} {p.currency.upper()}")
        if p.features:
            for feat in p.features:
                click.echo(f"  • {feat}")


@billing_group.command("invoices")
@pass_client
def invoices_cmd(client):
    """List past invoices."""
    invoices = client.billing.invoices()
    if not invoices:
        click.echo("No invoices found.")
        return
    click.echo(f"{'DATE':<12} {'AMOUNT':<10} {'CURRENCY':<10} {'STATUS':<12} RECEIPT")
    click.echo("-" * 65)
    for inv in invoices:
        amount = f"{inv.amount:.2f}" if inv.amount is not None else "N/A"
        date = (inv.date or "")[:10]
        receipt = inv.receipt_url or ""
        click.echo(f"{date:<12} {amount:<10} {(inv.currency or '').upper():<10} {(inv.status or ''):<12} {receipt}")


@billing_group.command("usage")
@click.option("--period", default=None, help="Period in YYYY-MM format (default: current).")
@pass_client
def usage_cmd(client, period):
    """Show credit usage for a billing period."""
    u = client.usage.get(period=period)
    consumed = u.credits_consumed if u.credits_consumed is not None else "N/A"
    limit = u.credits_limit if u.credits_limit is not None else "N/A"
    click.echo(f"Credits consumed: {consumed} / {limit}")
    if u.period_start:
        click.echo(f"Period:           {u.period_start[:10]} → {(u.period_end or '')[:10]}")
    if u.request_count is not None:
        click.echo(f"Requests:         {u.request_count}")
    if u.breakdown:
        click.echo("\nDaily breakdown:")
        click.echo(f"  {'DATE':<12} {'CREDITS':<10} REQUESTS")
        for row in u.breakdown:
            click.echo(
                f"  {str(row.get('date', '')):<12} "
                f"{str(row.get('credits', '')):<10} "
                f"{row.get('request_count', '')}"
            )


@billing_group.command("checkout")
@click.argument("plan", metavar="PLAN")
@click.option(
    "--interval",
    default="monthly",
    show_default=True,
    type=click.Choice(["monthly", "yearly"], case_sensitive=False),
    help="Billing interval.",
)
@click.option("--no-browser", is_flag=True, help="Print URL instead of opening browser.")
@pass_client
def checkout_cmd(client, plan: str, interval: str, no_browser: bool):
    """Create a checkout session and open Stripe. PLAN: pro, pro_plus, ultra."""
    url = client.billing.checkout(plan=plan.lower(), interval=interval.lower())
    if no_browser:
        click.echo(f"Open this URL to complete payment:\n{url.url}")
    else:
        click.echo("Opening browser to complete payment…")
        webbrowser.open(url.url)
        click.echo(f"If the browser did not open, visit:\n{url.url}")
