<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import { invites } from '$lib/api';
	import { authStore } from '$lib/stores/auth';
	import { ShieldCheck, Loader2 } from 'lucide-svelte';

	let token = '';
	let inviteData: { email: string; role: string; invited_by_name: string; expires_at: string; valid: boolean } | null = null;
	let loadingInvite = true;
	let inviteError = '';

	let validationCode = '';
	let username = '';
	let fullName = '';
	let password = '';
	let confirmPassword = '';
	let submitting = false;

	onMount(async () => {
		token = $page.url.searchParams.get('token') || '';
		if (!token) {
			inviteError = 'No invite token provided.';
			loadingInvite = false;
			return;
		}
		try {
			inviteData = await invites.validate(token);
			if (!inviteData?.valid) {
				inviteError = 'This invite has expired or has already been used.';
			}
		} catch (e: any) {
			inviteError = e.message || 'Invalid or expired invite link.';
		} finally {
			loadingInvite = false;
		}
	});

	async function handleAccept() {
		if (!inviteData?.valid) return;
		if (password !== confirmPassword) {
			toast.error('Passwords do not match');
			return;
		}
		if (password.length < 8) {
			toast.error('Password must be at least 8 characters');
			return;
		}
		submitting = true;
		try {
			await invites.accept({ token, validation_code: validationCode, username, full_name: fullName, password });
			await authStore.loadMe();
			toast.success('Account created! Welcome to TeamFlow.');
			goto('/');
		} catch (e: any) {
			toast.error(e.message || 'Failed to accept invite');
		} finally {
			submitting = false;
		}
	}
</script>

<svelte:head><title>Accept Invite · TeamFlow</title></svelte:head>

<div class="min-h-screen bg-gray-950 flex items-center justify-center p-4">
	<div class="w-full max-w-md">
		<div class="flex items-center gap-2.5 justify-center mb-8">
			<div class="w-9 h-9 bg-primary-600 rounded-lg flex items-center justify-center text-white font-bold text-base">T</div>
			<span class="font-semibold text-white text-xl">TeamFlow</span>
		</div>

		{#if loadingInvite}
			<div class="flex items-center justify-center py-16">
				<Loader2 class="animate-spin text-primary-400" size={32} />
			</div>
		{:else if inviteError}
			<div class="card text-center py-12">
				<ShieldCheck class="mx-auto text-gray-600 mb-4" size={40} />
				<h2 class="text-lg font-semibold text-white mb-2">Invalid Invite</h2>
				<p class="text-gray-400 text-sm mb-6">{inviteError}</p>
				<a href="/login" class="text-primary-400 text-sm hover:underline">Go to login</a>
			</div>
		{:else if inviteData}
			<div class="card">
				<div class="mb-6">
					<h1 class="text-xl font-bold text-white mb-1">Accept your invite</h1>
					<p class="text-gray-400 text-sm">
						<span class="text-white font-medium">{inviteData.invited_by_name}</span> invited you to join as
						<span class="text-primary-400 font-medium capitalize">{inviteData.role}</span>
					</p>
					<p class="text-gray-500 text-xs mt-1">Joining as: {inviteData.email}</p>
				</div>

				<form on:submit|preventDefault={handleAccept} class="space-y-4">
					<div>
						<label class="block text-sm font-medium text-gray-300 mb-1.5" for="code">
							Validation Code <span class="text-gray-500 font-normal">(from your email)</span>
						</label>
						<input
							id="code"
							type="text"
							bind:value={validationCode}
							required
							maxlength="6"
							placeholder="6-digit code"
							class="input w-full tracking-widest text-center text-lg font-mono"
						/>
					</div>

					<div>
						<label class="block text-sm font-medium text-gray-300 mb-1.5" for="fullName">Full Name</label>
						<input
							id="fullName"
							type="text"
							bind:value={fullName}
							required
							placeholder="Jane Smith"
							class="input w-full"
						/>
					</div>

					<div>
						<label class="block text-sm font-medium text-gray-300 mb-1.5" for="username">Username</label>
						<input
							id="username"
							type="text"
							bind:value={username}
							required
							placeholder="janesmith"
							class="input w-full"
						/>
					</div>

					<div>
						<label class="block text-sm font-medium text-gray-300 mb-1.5" for="password">Password</label>
						<input
							id="password"
							type="password"
							bind:value={password}
							required
							minlength="8"
							placeholder="At least 8 characters"
							class="input w-full"
						/>
					</div>

					<div>
						<label class="block text-sm font-medium text-gray-300 mb-1.5" for="confirm">Confirm Password</label>
						<input
							id="confirm"
							type="password"
							bind:value={confirmPassword}
							required
							placeholder="Repeat password"
							class="input w-full"
						/>
					</div>

					<button
						type="submit"
						disabled={submitting}
						class="btn-primary w-full flex items-center justify-center gap-2 py-2.5"
					>
						{#if submitting}
							<Loader2 class="animate-spin" size={16} />
							Creating account…
						{:else}
							Join TeamFlow
						{/if}
					</button>
				</form>

				<p class="text-center text-xs text-gray-500 mt-4">
					Already have an account? <a href="/login" class="text-primary-400 hover:underline">Log in</a>
				</p>
			</div>
		{/if}
	</div>
</div>
