const path = require('path');
const HtmlBundlerPlugin = require('html-bundler-webpack-plugin');
const TerserPlugin = require("terser-webpack-plugin");
const WebpackObfuscator = require('webpack-obfuscator');
const isProduction = process.env.NODE_ENV == 'production';

const config = {
    output: {
        path: path.resolve(__dirname, 'dist'),
    },
    devServer: {
        open: true,
        host: 'localhost',
    },
    plugins: [
        new HtmlBundlerPlugin({
            entry: {
                index: 'src/index.html'
            },
            js: {
                inline: true,
            },
            css: {
                inline: true,
            },
        }),
    ],
    module: {
        rules: [
            {
                test: /\.ts$/i,
                loader: 'ts-loader',
                exclude: ['/node_modules/'],
            },
            {
                test: /\.(eot|svg|ttf|woff|woff2|png|jpg|gif|webp|glb)$/i,
                type: 'asset/inline',
            },
        ],
    },
    resolve: {
        extensions: ['.ts', '.js'],
    },
    optimization: {
        minimize: isProduction,
        minimizer: [new TerserPlugin(), new WebpackObfuscator()],
    },
};

module.exports = () => {
    if (isProduction) {
        config.mode = 'production';
    } else {
        config.mode = 'development';
    }
    return config;
};
