import fs from 'fs';
import path from 'path';
import { Popup } from '@/types/popup';
import FeedItem from '@/components/FeedItem';

// Helper to get data
async function getPopups(): Promise<Popup[]> {
	try {
		const filePath = path.join(process.cwd(), 'public/data/popups.json');
		const fileContents = fs.readFileSync(filePath, 'utf8');
		return JSON.parse(fileContents);
	} catch (error) {
		console.error("Failed to read popups data:", error);
		return [];
	}
}

export default async function Home() {
	const popups = await getPopups();

	return (
		<main className="min-h-screen bg-gray-50 flex flex-col items-center py-8">
			<div className="w-full max-w-md">
				{/* Header */}
				<header className="flex justify-between items-center px-4 mb-6 sticky top-0 bg-gray-50 z-10 py-2">
					<h1 className="text-xl font-bold font-serif italic text-black">Daily Seongsu</h1>
					<div className="flex space-x-4">
						<button>
							<svg aria-label="Notifications" className="w-6 h-6" fill="none" height="24" role="img" viewBox="0 0 24 24" width="24"><path d="M16.792 3.904A4.989 4.989 0 0 1 21.5 9.122c0 3.072-2.652 4.956-5.197 7.222-2.512 2.243-3.865 3.469-4.303 3.752-.477-.309-2.143-1.823-4.303-3.752C5.141 14.072 2.5 12.167 2.5 9.122a4.989 4.989 0 0 1 4.708-5.218 4.21 4.21 0 0 1 3.675 1.941c.84 1.175.98 1.763 1.12 1.763s.278-.588 1.11-1.766a4.17 4.17 0 0 1 3.679-1.938m0-2a6.04 6.04 0 0 0-4.797 2.127 6.052 6.052 0 0 0-4.787-2.127A6.985 6.985 0 0 0 .5 9.122c0 3.61 2.55 5.827 5.015 7.97.283.246.569.494.853.747l1.027.918a44.998 44.998 0 0 0 3.518 3.018 2 2 0 0 0 2.174 0 45.263 45.263 0 0 0 3.626-3.115l.922-.824c.293-.26.59-.519.885-.774 2.334-2.025 4.98-4.32 4.98-7.94a6.985 6.985 0 0 0-6.708-7.218Z" fill="black"></path></svg>
						</button>
					</div>
				</header>

				{/* Feed */}
				<div className="flex flex-col">
					{popups.length > 0 ? (
						popups.map((popup) => (
							<FeedItem key={popup.id} popup={popup} />
						))
					) : (
						<div className="text-gray-500 text-center py-10">
							No pop-ups found today.
						</div>
					)}
				</div>
			</div>
		</main>
	);
}
