import tailwindcss from 'tailwindcss';
import autoprefixer from 'autoprefixer';

function unwrapLayerForNodeModules() {
	return {
		postcssPlugin: 'unwrap-layer-for-node-modules',
		Once(root, { result }) {
			const from = result.opts.from || '';
			if (!from.includes('node_modules')) return;
			root.walkAtRules('layer', (rule) => {
				rule.replaceWith(rule.nodes);
			});
		}
	};
}
unwrapLayerForNodeModules.postcss = true;

export default {
	plugins: [unwrapLayerForNodeModules(), tailwindcss(), autoprefixer()]
};
