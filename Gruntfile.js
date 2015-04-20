module.exports = function(grunt) {

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    uglify: {
      options: {
        mangle: false
      },
      build: {
        src: ['static/js/app/app.js', 'static/js/app/utils/*.js', 'static/js/app/directives/*.js', 'static/js/app/services/*.js', 'static/js/app/controllers/*.js'],
        dest: 'static/js/app/app.min.js'
      },
    },
    watch: {
      app: {
        files: ['static/js/app/app.js', 'static/js/app/utils/*.js', 'static/js/app/directives/*.js', 'static/js/app/services/*.js', 'static/js/app/controllers/*.js'],
        tasks: ['uglify']
      }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-uglify');

  grunt.registerTask('default', ['uglify', 'watch']);

};
