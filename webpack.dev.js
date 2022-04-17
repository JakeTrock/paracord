const path = require("path");
const webpack = require("webpack");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const { VueLoaderPlugin } = require("vue-loader");

module.exports = {
  devtool: "eval-cheap-module-source-map",
  entry: "./src/index.js",
  devServer: {
    port: 8000,
  },
  resolve: {
    fallback: {
      buffer: require.resolve("buffer/"),
      process: require.resolve("process/"),
    },
  },
  devServer: {
    historyApiFallback: true,
    allowedHosts: "all",
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        loader: "babel-loader",
        options: {
          presets: ["@babel/preset-env"],
        },
      },
      {
        test: /\.vue$/,
        use: "vue-loader",
      },
      {
        test: /\.(scss|css)$/,
        use: [
          {
            // creates style nodes from JS strings
            loader: "style-loader",
            options: {
              // sourceMap: true
            },
          },
          {
            // translates CSS into CommonJS
            loader: "css-loader",
            options: {
              // sourceMap: true
            },
          },
          {
            // compiles Sass to CSS
            loader: "sass-loader",
            options: {
              // outputStyle: 'expanded',
              // sourceMap: true,
              // sourceMapContents: true
            },
          },
          // Please note we are not running postcss here
        ],
      },
      {
        // Load all images as base64 encoding if they are smaller than 8192 bytes
        test: /\.(png|jpg|gif)$/,
        use: [
          {
            loader: "url-loader",
            options: {
              // On development we want to see where the file is coming from, hence we preserve the [path]
              name: "[path][name].[ext]?hash=[hash:20]",
              limit: 8192,
            },
          },
        ],
      },
      {
        // Load all icons
        test: /\.(eot|woff|woff2|svg|ttf)([\?]?.*)$/,
        use: [
          {
            loader: "file-loader",
          },
        ],
      },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: "./index.html",
      inject: true,
    }),
    new webpack.ProvidePlugin({
      process: "process/browser",
      Buffer: ["buffer", "Buffer"],
    }),
    new VueLoaderPlugin(),
  ],
};
