# Next.js 14와 React 18의 새로운 기능들

## 개요

Next.js 14와 React 18의 출시로 웹 개발 생태계에 많은 변화가 있었습니다. 이번 포스트에서는 주요 새 기능들과 개발자들이 알아야 할 핵심 사항들을 다루겠습니다.

### React 18의 핵심 기능

#### 1. Concurrent Features

React 18의 가장 큰 변화는 **Concurrent Features**입니다:

- **Automatic Batching**: 성능 개선을 위한 자동 배치 처리
- **Transitions**: 긴급하지 않은 업데이트 처리
- **Suspense Improvements**: 데이터 페칭의 개선된 처리

```jsx
import { startTransition } from 'react';

function App() {
  const [isPending, startTransition] = useTransition();
  const [input, setInput] = useState('');
  const [list, setList] = useState([]);

  const handleChange = (e) => {
    setInput(e.target.value);

    // 긴급하지 않은 업데이트를 transition으로 처리
    startTransition(() => {
      const newList = createLargeList(e.target.value);
      setList(newList);
    });
  };

  return (
    <div>
      <input value={input} onChange={handleChange} />
      {isPending && <div>Loading...</div>}
      <ExpensiveList list={list} />
    </div>
  );
}
```

#### 2. Server Components

서버 컴포넌트를 통한 성능 최적화:

```jsx
// app/page.tsx (서버 컴포넌트)
async function getData() {
  const res = await fetch('https://api.example.com/posts');
  if (!res.ok) {
    throw new Error('Failed to fetch data');
  }
  return res.json();
}

export default async function Page() {
  const posts = await getData();

  return (
    <main>
      <h1>블로그 포스트</h1>
      {posts.map(post => (
        <article key={post.id}>
          <h2>{post.title}</h2>
          <p>{post.excerpt}</p>
        </article>
      ))}
    </main>
  );
}
```

### Next.js 14의 새로운 기능들

#### App Router의 안정화

```typescript
// app/layout.tsx
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: '나의 블로그',
  description: 'Next.js 14로 만든 현대적인 블로그',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body>
        <header>
          <nav>네비게이션</nav>
        </header>
        <main>{children}</main>
        <footer>푸터</footer>
      </body>
    </html>
  );
}
```

#### 향상된 이미지 최적화

```jsx
import Image from 'next/image';

export default function ProfilePage() {
  return (
    <div>
      <Image
        src="/profile.jpg"
        alt="프로필 사진"
        width={500}
        height={500}
        priority
        placeholder="blur"
        blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
      />
    </div>
  );
}
```

## 성능 최적화 팁

### 1. 동적 임포트 활용

```javascript
import dynamic from 'next/dynamic';

// 클라이언트 사이드에서만 로드되는 컴포넌트
const DynamicChart = dynamic(
  () => import('../components/Chart'),
  {
    ssr: false,
    loading: () => <div>차트를 로딩중입니다...</div>
  }
);

export default function Dashboard() {
  return (
    <div>
      <h1>대시보드</h1>
      <DynamicChart />
    </div>
  );
}
```

### 2. API 라우트 최적화

```typescript
// app/api/posts/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const page = searchParams.get('page') || '1';

  try {
    const posts = await fetchPosts(parseInt(page));

    return NextResponse.json(
      { posts },
      {
        status: 200,
        headers: {
          'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=30'
        }
      }
    );
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch posts' },
      { status: 500 }
    );
  }
}
```

## 마이그레이션 가이드

### Pages Router에서 App Router로

1. **라우팅 구조 변경**
   ```
   pages/about.js → app/about/page.js
   pages/blog/[slug].js → app/blog/[slug]/page.js
   ```

2. **데이터 페칭 변경**
   ```jsx
   // 기존 (Pages Router)
   export async function getServerSideProps() {
     const data = await fetchData();
     return { props: { data } };
   }

   // 새로운 방식 (App Router)
   async function getData() {
     return await fetchData();
   }

   export default async function Page() {
     const data = await getData();
     return <div>{data.title}</div>;
   }
   ```

## 결론

Next.js 14와 React 18은 웹 개발의 새로운 패러다임을 제시합니다:

- ✅ 향상된 성능과 사용자 경험
- ✅ 더 나은 개발자 경험 (DX)
- ✅ 서버와 클라이언트의 최적화된 조합
- ✅ 타입스크립트 지원 강화

앞으로도 이러한 기술들의 발전을 주시하며, 실제 프로젝트에 적용해보는 것을 추천합니다.

---

*참고 자료:*
- [React 18 공식 문서](https://react.dev/)
- [Next.js 14 릴리즈 노트](https://nextjs.org/blog/next-14)
- [Vercel 성능 가이드](https://vercel.com/docs)
