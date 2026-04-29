<script lang="ts">
	import { auth } from '$lib/apis';
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';

	let form = { email: '', username: '', full_name: '', password: '', role: 'member' };
	let loading = false;

	async function handleRegister() {
		loading = true;
		try {
			await auth.register(form);
			toast.success('Account created! Please sign in.');
			goto('/login');
		} catch (e: any) {
			toast.error(e.message || 'Registration failed');
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head><title>Register · TeamFlow</title></svelte:head>

<div class="min-h-screen bg-gray-950 flex items-center justify-center p-4">
	<div class="w-full max-w-sm">
		<div class="text-center mb-8">
			<div class="w-12 h-12 bg-primary-600 rounded-xl flex items-center justify-center text-white font-bold text-xl mx-auto mb-4">T</div>
			<h1 class="text-2xl font-bold text-white">Create account</h1>
			<p class="text-gray-400 mt-1 text-sm">Join TeamFlow</p>
		</div>

		<form on:submit|preventDefault={handleRegister} class="card space-y-4">
			<div>
				<label class="label" for="fullname">Full Name</label>
				<input id="fullname" bind:value={form.full_name} type="text" class="input" placeholder="Jane Doe" required />
			</div>
			<div>
				<label class="label" for="email">Email</label>
				<input id="email" bind:value={form.email} type="email" class="input" placeholder="jane@example.com" required />
			</div>
			<div>
				<label class="label" for="username">Username</label>
				<input id="username" bind:value={form.username} type="text" class="input" placeholder="jane_doe" required />
			</div>
			<div>
				<label class="label" for="password">Password</label>
				<input id="password" bind:value={form.password} type="password" class="input" placeholder="••••••••" required />
			</div>
			<div>
				<label class="label" for="role">Role</label>
				<select id="role" bind:value={form.role} class="input">
					<option value="member">Member</option>
					<option value="supervisor">Supervisor</option>
					<option value="assistant_manager">Assistant Manager</option>
					<option value="manager">Manager</option>
				</select>
			</div>
			<button type="submit" class="btn-primary w-full justify-center" disabled={loading}>
				{#if loading}<span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>{/if}
				Create Account
			</button>
		</form>

		<p class="text-center text-sm text-gray-500 mt-4">
			Already have an account? <a href="/login" class="text-primary-400 hover:text-primary-300">Sign in</a>
		</p>
	</div>
</div>
