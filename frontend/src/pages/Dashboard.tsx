import { useEffect, useMemo, useState } from 'react';
import { Eyebrow } from '@/components/Eyebrow';
import { StatusDot } from '@/components/StatusDot';
import { SectionHeading } from '@/components/SectionHeading';
import { IndicatorCards } from '@/components/IndicatorCards';
import { StatusCountsTable } from '@/components/StatusCountsTable';
import { RecentActivityFeed } from '@/components/RecentActivityFeed';
import { ActiveReviewsList } from '@/components/ActiveReviewsList';
import { UpcomingReleasesTable } from '@/components/UpcomingReleasesTable';
import { DeadlinesTable } from '@/components/DeadlinesTable';
import { ManuscriptListItem } from '@/components/ManuscriptListItem';
import { fetchHealth, fetchMeta } from '@/api/meta';
import { fetchManuscripts } from '@/api/manuscripts';
import {
  fetchActiveReviews,
  fetchDeadlines,
  fetchRecentActivity,
  fetchStatusCounts,
  fetchUpcomingReleases,
} from '@/api/dashboard';
import type { AppMeta } from '@/types/meta';
import type { Manuscript } from '@/types/manuscript';
import type {
  ActiveReviewSummary,
  ActivityEntry,
  DeadlineEntry,
  StatusCount,
  UpcomingRelease,
} from '@/types/dashboard';

type ServiceState = 'pending' | 'ok' | 'error';

interface DashboardProps {
  onOpenManuscript: (id: string) => void;
}

export function Dashboard({ onOpenManuscript }: DashboardProps) {
  const [meta, setMeta] = useState<AppMeta | null>(null);
  const [service, setService] = useState<ServiceState>('pending');
  const [manuscripts, setManuscripts] = useState<Manuscript[] | null>(null);
  const [statusCounts, setStatusCounts] = useState<StatusCount[]>([]);
  const [activeReviews, setActiveReviews] = useState<ActiveReviewSummary[]>([]);
  const [upcomingReleases, setUpcomingReleases] = useState<UpcomingRelease[]>([]);
  const [deadlines, setDeadlines] = useState<DeadlineEntry[]>([]);
  const [recentActivity, setRecentActivity] = useState<ActivityEntry[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([
      fetchMeta(),
      fetchHealth(),
      fetchManuscripts({ limit: 50 }),
      fetchStatusCounts(),
      fetchActiveReviews(),
      fetchUpcomingReleases(),
      fetchDeadlines(),
      fetchRecentActivity(),
    ])
      .then(([m, , page, counts, reviews, releases, due, activity]) => {
        if (cancelled) return;
        setMeta(m);
        setService('ok');
        setManuscripts(page.items);
        setStatusCounts(counts);
        setActiveReviews(reviews);
        setUpcomingReleases(releases);
        setDeadlines(due);
        setRecentActivity(activity);
      })
      .catch((e) => {
        if (cancelled) return;
        setService('error');
        setError(e instanceof Error ? e.message : 'Failed to load dashboard.');
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const indicators = useMemo(() => {
    const totals = statusCounts.reduce<Record<string, number>>((acc, c) => {
      acc[c.status] = c.count;
      return acc;
    }, {});
    const total = statusCounts.reduce((sum, c) => sum + c.count, 0);
    const underReview = totals['under_review'] ?? 0;
    const inProduction =
      (totals['layout'] ?? 0) +
      (totals['cover_design'] ?? 0) +
      (totals['prepress'] ?? 0);
    const overdue = deadlines.filter((d) => d.days_until < 0).length;
    return { total, underReview, inProduction, overdue };
  }, [statusCounts, deadlines]);

  const serviceLabel =
    service === 'ok' ? 'Connected' : service === 'error' ? 'Offline' : 'Probing';

  return (
    <div className="flex flex-col gap-20">
      <section className="grid grid-cols-1 gap-10 lg:grid-cols-[2fr,1fr]">
        <div>
          <Eyebrow>Prospectus</Eyebrow>
          <h2 className="mt-3 font-serif text-5xl leading-tight text-parchment">
            A quiet workshop for the long work of publishing.
          </h2>
          <p className="mt-6 max-w-prose text-parchment-muted">
            LOGOSFORGE assembles the daily ledger of an editorial house —
            manuscripts, authors, contracts, and the slow choreography of
            production — under a single, local, archival surface.
          </p>
        </div>

        <aside className="border-l border-rule pl-8">
          <Eyebrow>Colophon</Eyebrow>
          <dl className="mt-4 space-y-4 font-mono text-[0.78rem] uppercase tracking-wider text-parchment-muted">
            <div className="flex items-baseline justify-between gap-4">
              <dt className="text-parchment-dim">Service</dt>
              <dd>
                <StatusDot
                  tone={service === 'ok' ? 'ok' : service === 'error' ? 'error' : 'pending'}
                  label={serviceLabel}
                />
              </dd>
            </div>
            <div className="flex items-baseline justify-between gap-4">
              <dt className="text-parchment-dim">Edition</dt>
              <dd>{meta?.version ?? '—'}</dd>
            </div>
            <div className="flex items-baseline justify-between gap-4">
              <dt className="text-parchment-dim">Environment</dt>
              <dd>{meta?.environment ?? '—'}</dd>
            </div>
            <div className="flex items-baseline justify-between gap-4">
              <dt className="text-parchment-dim">Manuscripts</dt>
              <dd>{manuscripts?.length ?? '—'}</dd>
            </div>
          </dl>
        </aside>
      </section>

      {error && (
        <p className="font-mono text-[0.7rem] uppercase tracking-widest text-signal">
          {error}
        </p>
      )}

      <IndicatorCards
        total={indicators.total}
        underReview={indicators.underReview}
        inProduction={indicators.inProduction}
        overdue={indicators.overdue}
      />

      <section className="grid grid-cols-1 gap-14 lg:grid-cols-[1fr,1fr]">
        <div>
          <SectionHeading
            eyebrow="Ledger"
            title="Manuscripts by status"
            meta={`${indicators.total} on file`}
          />
          <div className="mt-6">
            <StatusCountsTable counts={statusCounts} />
          </div>
        </div>

        <div>
          <SectionHeading
            eyebrow="Chronicle"
            title="Recent workflow activity"
            meta={
              recentActivity.length === 0
                ? 'Nothing yet'
                : `${recentActivity.length} ${recentActivity.length === 1 ? 'entry' : 'entries'}`
            }
          />
          <div className="mt-8">
            <RecentActivityFeed
              entries={recentActivity}
              onOpenManuscript={onOpenManuscript}
            />
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-14 lg:grid-cols-[1fr,1fr]">
        <div>
          <SectionHeading
            eyebrow="Reading"
            title="Active reviews"
            meta={
              activeReviews.length === 0
                ? 'None'
                : `${activeReviews.length} manuscript${activeReviews.length === 1 ? '' : 's'}`
            }
          />
          <div className="mt-6">
            <ActiveReviewsList
              entries={activeReviews}
              onOpenManuscript={onOpenManuscript}
            />
          </div>
        </div>

        <div>
          <SectionHeading
            eyebrow="Forthcoming"
            title="Upcoming releases"
            meta={
              upcomingReleases.length === 0
                ? 'None scheduled'
                : `${upcomingReleases.length} in late production`
            }
          />
          <div className="mt-6">
            <UpcomingReleasesTable
              entries={upcomingReleases}
              onOpenManuscript={onOpenManuscript}
            />
          </div>
        </div>
      </section>

      <section>
        <SectionHeading
          eyebrow="Calendar"
          title="Deadlines"
          meta={
            deadlines.length === 0
              ? 'None outstanding'
              : `${indicators.overdue > 0 ? `${indicators.overdue} overdue · ` : ''}${deadlines.length} open`
          }
        />
        <div className="mt-6">
          <DeadlinesTable
            entries={deadlines}
            onOpenManuscript={onOpenManuscript}
          />
        </div>
      </section>

      <section>
        <div className="flex items-baseline justify-between">
          <Eyebrow>Manuscripts in the house</Eyebrow>
          <span className="font-mono text-[0.65rem] uppercase tracking-widest text-parchment-dim">
            Most recent first
          </span>
        </div>

        <div className="mt-6 border-t border-rule">
          {manuscripts === null && !error && (
            <p className="py-10 font-mono text-[0.7rem] uppercase tracking-widest text-parchment-dim">
              Loading…
            </p>
          )}
          {manuscripts !== null && manuscripts.length === 0 && (
            <p className="py-10 font-mono text-[0.7rem] uppercase tracking-widest text-parchment-dim">
              No manuscripts on the desk.
            </p>
          )}
          {manuscripts?.map((m) => (
            <ManuscriptListItem
              key={m.id}
              manuscript={m}
              onOpen={onOpenManuscript}
            />
          ))}
        </div>
      </section>
    </div>
  );
}
