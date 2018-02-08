var path = require("path");
var webpack = require("webpack");

module.exports = {
  entry: {
    app: [
      './src/index.js'
    ]
  },

  output: {
    path: path.resolve(__dirname + '/build'),
    filename: 'bundle.js'
  },

  module: {
    loaders: [
      {
        test: /\.(css|scss)$/,
        loaders: [
          'style-loader',
          'css-loader',
        ]
      },
    ]
  },
  plugins: [
  ],

  devServer: {
    inline: true,
    stats: { colors: true }
  }

};
