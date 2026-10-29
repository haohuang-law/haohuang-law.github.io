'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { TextPageConfig } from '@/types/page';

interface TextPageProps {
    config: TextPageConfig;
    content: string;
    embedded?: boolean;
}

export default function TextPage({ config, content, embedded = false }: TextPageProps) {
    const isCv = config.source === 'cv.md';
    const pdfUrl = '/CV_Hao%20Huang.pdf';
    const [hasCvPdf, setHasCvPdf] = useState(false);

    useEffect(() => {
        if (!isCv) return;
        const controller = new AbortController();
        fetch(pdfUrl, { method: 'HEAD', signal: controller.signal })
            .then(response => setHasCvPdf(response.ok && (response.headers.get('content-type') || '').includes('pdf')))
            .catch(() => setHasCvPdf(false));
        return () => controller.abort();
    }, [isCv]);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className={embedded ? "" : "max-w-3xl mx-auto"}
        >
            <h1 className={`${embedded ? "text-2xl" : "text-4xl"} font-serif font-bold text-primary mb-4`}>{config.title}</h1>
            {config.description && (
                <p className={`${embedded ? "text-base" : "text-lg"} text-neutral-600 dark:text-neutral-500 mb-8 max-w-2xl`}>
                    {config.description}
                </p>
            )}
            {isCv && hasCvPdf && (
                <div className="space-y-5">
                    <div className="flex flex-wrap gap-4">
                        <a href={pdfUrl} target="_blank" rel="noopener noreferrer" className="inline-flex items-center rounded-lg bg-accent px-5 py-2.5 font-medium text-white hover:bg-accent-dark transition-colors">Open PDF</a>
                        <a href={pdfUrl} download="CV_Hao_Huang.pdf" className="inline-flex items-center rounded-lg border border-accent px-5 py-2.5 font-medium text-accent hover:bg-accent/10 transition-colors">Download CV</a>
                    </div>
                    <iframe src={pdfUrl} title="Hao Huang Curriculum Vitae (PDF)" className="w-full h-[75vh] min-h-[600px] rounded-lg border border-neutral-200 dark:border-neutral-700" />
                </div>
            )}
            {(!isCv || !hasCvPdf) && <div className="text-neutral-700 dark:text-neutral-600 leading-relaxed">
                <ReactMarkdown
                    components={{
                        h1: ({ children }) => <h1 className="text-3xl font-serif font-bold text-primary mt-8 mb-4">{children}</h1>,
                        h2: ({ children }) => <h2 className="text-2xl font-serif font-bold text-primary mt-8 mb-4 border-b border-neutral-200 dark:border-neutral-800 pb-2">{children}</h2>,
                        h3: ({ children }) => <h3 className="text-xl font-semibold text-primary mt-6 mb-3">{children}</h3>,
                        p: ({ children }) => <p className="mb-4 last:mb-0">{children}</p>,
                        ul: ({ children }) => <ul className="list-disc list-inside mb-4 space-y-1 ml-4">{children}</ul>,
                        ol: ({ children }) => <ol className="list-decimal list-inside mb-4 space-y-1 ml-4">{children}</ol>,
                        li: ({ children }) => <li className="mb-1">{children}</li>,
                        a: ({ ...props }) => (
                            <a
                                {...props}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-accent font-medium transition-all duration-200 rounded hover:bg-accent/10 hover:shadow-sm"
                            />
                        ),
                        blockquote: ({ children }) => (
                            <blockquote className="border-l-4 border-accent/50 pl-4 italic my-4 text-neutral-600 dark:text-neutral-500">
                                {children}
                            </blockquote>
                        ),
                        strong: ({ children }) => <strong className="font-semibold text-primary">{children}</strong>,
                        em: ({ children }) => <em className="italic text-neutral-600 dark:text-neutral-500">{children}</em>,
                    }}
                >
                    {content}
                </ReactMarkdown>
            </div>}
        </motion.div>
    );
}
